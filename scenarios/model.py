"""Year-by-year electrification model for EMT Madrid, 2026-2035, at line and depot level.

simulate(params, L, fleet, name) -> (years, depots, depot_years, lines)

Each year:
 1. Buses are delivered (scenario schedule, capped by max_intake and, if set, by a yearly budget).
    Electric buses that reach bus_life are renewed first, like for like.
 2. New zero-emission buses join a pool. Whole CNG lines convert in priority order when the pool
    covers the line's buses AND its depot can charge the line at night (hydrogen lines need
    station capacity instead).
 3. Each converted line retires the same number of CNG buses, oldest first. CNG buses younger than
    bus_life count as scrapped early (book value lost, resale recovered, embodied CO2 wasted).
 4. Depot night capacity grows when a grid upgrade or a battery comes into service.
 5. Energy, gas, CO2, NOx, riders, opex, capex and NPV are accounted from the lines actually converted.
"""
import math
import numpy as np
import pandas as pd

YEARS = list(range(2026, 2041))   # simulated to 2040 so the 100 % year is found; money and CO2 reported 2026-2035
WINDOW_END = 2035
DEPOTS = ["Fuencarral", "Carabanchel", "Sanchinarro", "Entrevias", "La Elipa"]


def load_inputs(line_csv, fleet_csv, riders_csv=None, calendar_csv=None):
    L = pd.read_csv(line_csv, dtype={"line_code": str})
    L = L[["line_code", "line_label", "daily_km", "peak_buses", "depot_name", "technology", "bus_type",
           "km_per_bus_day", "line_energy_kwh_day", "charging_strategy"]].copy()
    L["riders_day"] = 0.0
    if riders_csv and calendar_csv:
        r = pd.read_csv(riders_csv, sep=";", dtype={"Linea": str})
        c = pd.read_csv(calendar_csv, dtype=str, keep_default_na=False)
        working = set(c.loc[c.TipoDiaEs == "LA", "Fecha"])
        rd = r[r.Fecha.isin(working)].groupby(["Linea", "Fecha"]).TotalViajeros.sum().groupby("Linea").mean()
        L["riders_day"] = L.line_code.map(rd).fillna(0.0)
    f = pd.read_csv(fleet_csv, dtype=str).apply(lambda col: col.str.strip()).drop_duplicates()
    last = f.sort_values(["vehicleId", "dateIni"]).groupby("vehicleId").tail(1)
    first = f.groupby("vehicleId").dateIni.min()
    a = last[last.dateEnd.isna() | (last.dateEnd >= "2025-12-31")].copy()
    a["year"] = a.vehicleId.map(first).str[:4].astype(int)
    a["fuel"] = a.fuelType.map({"GN": "CNG", "EL": "BEV", "H": "H2"})
    a["size"] = np.where(a.typeCapacity == "02", "Articulated", "Standard")
    fleet = a.groupby(["fuel", "size", "year"]).size().rename("n").reset_index()
    return L, fleet


def simulate(p, L, fleet, name="scenario"):
    p = dict(p)
    if p.get("flexible_access"):
        p["grid_lead_years"], p["grid_upgrade_eur"] = 2, 2_000_000
    L = L.copy()
    fleet_total0 = int(fleet.n.sum())
    spare = fleet_total0 / L.peak_buses.sum()                       # buses owned per peak bus
    L["need"] = np.maximum(1, np.round(L.peak_buses * spare)).astype(int)
    L["E_grid"] = L.line_energy_kwh_day / 1000 / p["charge_eff"]    # MWh a night from the grid if electric
    L["over_range"] = L.charging_strategy.ne("Depot")
    L["tech_target"] = np.where(L.over_range & (p["over_range_tech"] == "H2"), "H2", "BEV")
    L["converted"] = L.technology.isin(["BEV", "H2"])
    L["tech_now"] = np.where(L.converted, L.technology, "CNG")
    L["year_converted"] = np.where(L.converted, 2025, np.nan)
    L["h2_kg_day"] = L.daily_km * p["h2_kg_100km"] / 100

    order = p.get("order", "km_per_bus_desc")
    if order == "km_per_bus_desc":
        L["_k"] = L.over_range.astype(int) * 1e6 - L.km_per_bus_day
    elif order == "short_first":
        L["_k"] = L.over_range.astype(int) * 1e6 + L.km_per_bus_day
    elif order == "depot_sequence":
        rank = {d: i for i, d in enumerate(p.get("depot_sequence", DEPOTS))}
        L["_k"] = L.depot_name.map(rank) * 1e4 - L.km_per_bus_day
    elif order == "riders_desc":
        L["_k"] = L.over_range.astype(int) * 1e9 - L.riders_day
    L = L.sort_values("_k")

    host = lambda dep, y: "Fuencarral" if (dep == "La Elipa" and y < p["la_elipa_open"]) else dep

    cng = {(r.size, r.year): r.n for r in fleet[fleet.fuel == "CNG"].itertuples()}
    ze = {(r.fuel, r.year): r.n for r in fleet[fleet.fuel != "CNG"].itertuples()}

    bev_lines = L.converted & L.technology.eq("BEV")
    load0 = L[bev_lines].assign(h=L.depot_name.map(lambda d: host(d, 2026))).groupby("h").E_grid.sum()
    cap_mw = {}
    for d in DEPOTS:
        v = p["depot_mw_today"].get(d)
        cap_mw[d] = max(v if v is not None else 0.0, load0.get(d, 0.0) / p["window_h"])
    points = dict(p["depot_points_today"])

    final_E = L[L.tech_target.eq("BEV")].groupby("depot_name").E_grid.sum().to_dict()
    strategy = p.get("power", "grid")
    upgrades, batteries = {}, {}
    if strategy in ("grid", "bess+grid"):
        for d in DEPOTS:
            need_mw = final_E.get(d, 0) / p["window_h"]
            if d != "La Elipa" and need_mw > cap_mw[d] + 1e-9:
                upgrades[d] = dict(order=p["decision_year"], ready=p["decision_year"] + p["grid_lead_years"],
                                   add_mw=need_mw - cap_mw[d])
    if strategy in ("bess", "bess+grid"):
        for d in DEPOTS:
            if d == "La Elipa":
                continue
            short = final_E.get(d, 0) - cap_mw[d] * p["window_h"]
            if short > 1e-9:
                max_out = cap_mw[d] * (24 - p["window_h"]) * p["bess_rt_eff"]
                out = min(short, max_out)
                batteries[d] = dict(order=p["decision_year"], ready=p["decision_year"] + p["bess_lead_years"],
                                    out_mwh=out, nameplate_mwh=out / p["bess_dod"], unbridged_mwh=short - out)

    def capE(d, y):
        mw = cap_mw[d]
        if d == "La Elipa":
            mw = p["la_elipa_mw"] if y >= p["la_elipa_open"] else 0.0
        if d in upgrades and y >= upgrades[d]["ready"]:
            mw += upgrades[d]["add_mw"]
        e = mw * p["window_h"]
        if d in batteries and y >= batteries[d]["ready"] and not (d in upgrades and y >= upgrades[d]["ready"]):
            e += batteries[d]["out_mwh"]
        return e

    # hydrogen station capacity: Entrevias' station already serves line 145
    h2_cap = p["h2_station_kg_day"]
    h2_used = float(L[L.converted & L.technology.eq("H2")].h2_kg_day.sum())

    def co2_rows(rows):
        km = rows.daily_km * p["service_days"]
        cng_rows = rows.tech_now.eq("CNG"); bev_rows = rows.tech_now.eq("BEV")
        c = (km[cng_rows] * rows.bus_type[cng_rows].map(p["cng_kg_km"]) * p["cng_kgco2_per_kg"] / 1000).sum()
        e = (km[bev_rows] * rows.bus_type[bev_rows].map(p["kwh_km"]) / p["charge_eff"] * p["grid_gco2_kwh"] / 1e6).sum()
        return float(c + e)
    co2_cf = co2_rows(L)

    pool = 0
    rows, dep_rows = [], []
    sched = p["deliveries"]
    for y in YEARS:
        # ---- power capex this year (orders), needed first for the budget cap
        capex_grid = sum(p["grid_upgrade_eur"] for u in upgrades.values() if u["order"] == y)
        capex_bess = sum(b["nameplate_mwh"] * 1000 * p["bess_eur_kwh"] for b in batteries.values() if b["order"] == y)

        # ---- 1. deliveries and renewals
        due_ze = sum(n for (fu, yr), n in ze.items() if y - yr >= p["bus_life"])
        due_cng = sum(n for (s, yr), n in cng.items() if y - yr >= p["bus_life"])
        need_left = int(L.loc[~L.converted, "need"].sum())
        state = dict(cng_left=need_left, due_ze=due_ze, due_cng=due_cng, pool=pool, year=y)
        want = sched(y, state) if callable(sched) else sched.get(y, 0)
        n_cng_left = sum(cng.values())
        # a plan that means to retire every gas bus left also buys the few extra buses whole lines need (rounding)
        if n_cng_left and want - due_ze >= n_cng_left - pool:
            want = max(want, due_ze + max(0, need_left - pool))
        # buses reaching the maximum age must go; EMT buys no more gas buses, so they are replaced by electric
        forced = sum(n for (s, yr), n in cng.items() if y - yr >= p["max_age"])
        want = max(want, due_ze + max(0, forced - pool))
        if forced and forced >= n_cng_left:
            want = max(want, due_ze + max(0, need_left - pool))
        want += p["order_2026"].get(y, 0)
        cap = p["max_intake"] if y >= p["first_order_delivery"] else p["order_2026"].get(y, 0)
        if p.get("budget_cap_meur") and y >= p["first_order_delivery"]:
            room = p["budget_cap_meur"] * 1e6 - (capex_grid + capex_bess) * (1 - p["grant_share_infra"])
            cap = min(cap, max(0, int(room // (p["bus_price"]["Standard"] + p["charger_eur"]))))
        delivered = int(max(0, min(want, cap)))
        # power-aware delivery: new buses only arrive if a depot can charge the lines they would run
        # (buses forced by the maximum age always arrive). The rest are deferred to later years.
        deferred = 0
        if p.get("power_aware", True) and y >= p["first_order_delivery"]:
            tl = {d: float(L[L.converted & L.tech_now.eq("BEV") & L.depot_name.map(lambda x: host(x, y)).eq(d)].E_grid.sum())
                  for d in DEPOTS}
            useful, h2_t = 0, h2_used
            for r in L[~L.converted].itertuples():
                h = host(r.depot_name, y)
                if r.tech_target == "H2":
                    useful += r.need; continue
                if tl[h] + r.E_grid <= capE(h, y) + 1e-9:
                    tl[h] += r.E_grid; useful += r.need
            allowed_new = max(useful - pool, forced - pool, 0)
            new_wanted = delivered - min(due_ze, delivered)
            if new_wanted > allowed_new:
                deferred = new_wanted - allowed_new
                delivered -= deferred
        renew = min(due_ze, delivered)
        left = renew
        for k in sorted(ze, key=lambda k: k[1]):
            if left == 0:
                break
            if y - k[1] >= p["bus_life"]:
                t = min(ze[k], left); ze[k] -= t; left -= t
                ze[(k[0], y)] = ze.get((k[0], y), 0) + t
        new = delivered - renew
        pool += new
        capex_bus = delivered * p["bus_price"]["Standard"]

        # ---- 2. convert whole lines
        loads = {d: float(L[L.converted & L.tech_now.eq("BEV") & L.depot_name.map(lambda x: host(x, y)).eq(d)].E_grid.sum())
                 for d in DEPOTS}
        if y == p["la_elipa_open"]:
            points["La Elipa"] = points.get("La Elipa", 0) + p["la_elipa_points"]
        conv_now, capex_chg, capex_h2, cng_retired, early, stranded, art_retired, wasted_t = [], 0.0, 0.0, 0, 0, 0.0, 0, 0.0
        new_h2_buses = 0
        blocked = set()
        for idx, r in L[~L.converted].iterrows():
            if pool < r.need:
                continue
            h = host(r.depot_name, y)
            if r.tech_target == "H2":
                if h2_used + r.h2_kg_day > h2_cap + 1e-9:
                    if y >= p["decision_year"] + 2:          # a new station takes about 2 years (assumption)
                        h2_cap += p["h2_station_kg_day"]; capex_h2 += p["h2_station_eur"]
                    else:
                        blocked.add("H2 station"); continue
                h2_used += r.h2_kg_day
                capex_h2 += r.need * (p["h2_bus_eur"] - p["bus_price"]["Standard"])
                new_h2_buses += r.need
            else:
                if loads[h] + r.E_grid > capE(h, y) + 1e-9:
                    blocked.add(h); continue
                loads[h] += r.E_grid
                use = min(points.get(h, 0), r.need)
                points[h] = points.get(h, 0) - use
                capex_chg += (r.need - use) * p["charger_eur"]
                if r.over_range:
                    capex_chg += p["opp_charger_eur"]
            pool -= r.need
            L.at[idx, "converted"] = True
            L.at[idx, "tech_now"] = r.tech_target
            L.at[idx, "year_converted"] = y
            conv_now.append(r.line_label)
            left = r.need
            for k in sorted(cng, key=lambda k: k[1]):
                if left == 0:
                    break
                t = min(cng[k], left)
                if t == 0:
                    continue
                cng[k] -= t; left -= t; cng_retired += t
                age = y - k[1]
                if k[0] == "Articulated":
                    art_retired += t
                if age < p["bus_life"]:
                    early += t
                    frac = (p["bus_life"] - age) / p["bus_life"]
                    stranded += t * p["cng_book_price"] * frac
                    wasted_t += t * p["embodied_t"]["CNG"] * frac
        if L.converted.all():
            for k in list(cng):
                t = cng[k]
                if t:
                    age = y - k[1]
                    if age < p["bus_life"]:
                        early += t
                        frac = (p["bus_life"] - age) / p["bus_life"]
                        stranded += t * p["cng_book_price"] * frac
                        wasted_t += t * p["embodied_t"]["CNG"] * frac
                    if k[0] == "Articulated":
                        art_retired += t
                    cng[k] = 0; cng_retired += t
        ze[("BEV", y)] = ze.get(("BEV", y), 0) + new - new_h2_buses
        if new_h2_buses:
            ze[("H2", y)] = ze.get(("H2", y), 0) + new_h2_buses
        capex_bus += art_retired * (p["bus_price"]["Articulated"] - p["bus_price"]["Standard"])

        # ---- 3. other capex
        capex_elipa = p["la_elipa_capex_eur"] / 3 if p["la_elipa_open"] - 3 <= y <= p["la_elipa_open"] - 1 else 0.0
        swaps = sum(n for (fu, yr), n in ze.items() if fu == "BEV" and y - yr == p["bev_battery_swap_age"])
        capex_swap = swaps * p["bev_battery_swap_eur"]
        infra = capex_chg + capex_grid + capex_bess
        grants = infra * p["grant_share_infra"]

        # ---- 4. energy, gas, CO2, NOx, riders, opex
        km_yr = L.daily_km * p["service_days"]
        is_bev, is_h2, is_cng = L.tech_now.eq("BEV"), L.tech_now.eq("H2"), L.tech_now.eq("CNG")
        elec_mwh = float((km_yr[is_bev] * L.bus_type[is_bev].map(p["kwh_km"]) / p["charge_eff"]).sum() / 1000)
        cng_kg = float((km_yr[is_cng] * L.bus_type[is_cng].map(p["cng_kg_km"])).sum())
        gas_gwh = cng_kg * p["gas_kwh_per_kg"] / 1e6
        h2_kg = float((km_yr[is_h2] * p["h2_kg_100km"] / 100).sum())
        co2 = co2_rows(L)
        nox_t = float(km_yr[is_cng].sum() * p["nox_g_km_cng"] / 1e6)
        tender = p["gas_tender_gwh_yr"].get(y, 0)
        top_cost = max(0.0, p["gas_take_or_pay"] * tender - gas_gwh) * 1000 * p["gas_price_eur_mwh"] if tender else 0.0
        opex_energy = elec_mwh * p["elec_price_eur_mwh"] + gas_gwh * 1000 * p["gas_price_eur_mwh"] + h2_kg * p["h2_price_eur_kg"]
        opex_maint = float(km_yr[is_cng].sum() * p["maint_eur_km"]["CNG"] + km_yr[is_bev].sum() * p["maint_eur_km"]["BEV"]
                           + km_yr[is_h2].sum() * p["maint_eur_km"]["H2"])
        riders_e = float(L.loc[~is_cng, "riders_day"].sum() / max(L.riders_day.sum(), 1) * 100)

        n_cng = sum(cng.values()); n_ze = sum(ze.values())
        n_h2 = sum(n for (fu, _), n in ze.items() if fu == "H2")
        overage = sum(n for (s, yr), n in cng.items() if y - yr > p["bus_life"])
        over_max = sum(n for (s, yr), n in cng.items() if y - yr >= p["max_age"])
        if y == WINDOW_END:   # fleet value left at end-2035 (straight-line), credited in net cost and NPV
            price_v = {"BEV": p["bus_price"]["Standard"], "H2": p["h2_bus_eur"]}
            value_2035 = sum(n * price_v[fu] * max(0, p["bus_life"] - (2035 - yr)) / p["bus_life"] for (fu, yr), n in ze.items())
            value_2035 += sum(n * p["cng_book_price"] * max(0, p["bus_life"] - (2035 - yr)) / p["bus_life"] for (s, yr), n in cng.items())
        capex_total = capex_bus + capex_chg + capex_grid + capex_bess + capex_elipa + capex_h2 + capex_swap - grants
        rows.append(dict(
            scenario=name, year=y, delivered=delivered, renewals=renew, new_ze=new,
            fleet_total=n_cng + n_ze, n_bev=n_ze - n_h2, n_h2=n_h2, n_ze=n_ze, n_cng=n_cng,
            ze_share_pct=round(100 * n_ze / (n_cng + n_ze), 1),
            lines_electric=int(L.converted.sum()), lines_converted_this_year=len(conv_now),
            km_share_electric_pct=round(100 * L[L.converted].daily_km.sum() / L.daily_km.sum(), 1),
            riders_ze_lines_pct=round(riders_e, 1),
            idle_ze=int(pool), deferred_for_power=deferred, cng_retired=cng_retired, early_scrapped=early, cng_over_life=overage, cng_over_max_age=over_max,
            electricity_mwh=round(elec_mwh), gas_gwh=round(gas_gwh, 1), gas_tender_gwh=tender, h2_t=round(h2_kg / 1000, 1),
            cng_t=round(cng_kg / 1000), co2_t=round(co2), co2_avoided_t=round(co2_cf - co2), nox_t=round(nox_t, 1),
            embodied_new_t=round((delivered) * p["embodied_t"]["BEV"]), embodied_wasted_t=round(wasted_t),
            capex_buses_meur=capex_bus / 1e6, capex_chargers_meur=capex_chg / 1e6, capex_grid_meur=capex_grid / 1e6,
            capex_bess_meur=capex_bess / 1e6, capex_h2_meur=capex_h2 / 1e6, capex_battery_swaps_meur=capex_swap / 1e6,
            capex_la_elipa_meur=capex_elipa / 1e6, grants_meur=grants / 1e6, capex_total_meur=capex_total / 1e6,
            emt_invest_ref_meur=p["emt_invest_meur"].get(y, p["emt_invest_meur"][max(p["emt_invest_meur"])]),
            opex_energy_meur=opex_energy / 1e6, opex_maint_meur=opex_maint / 1e6,
            stranded_meur=stranded / 1e6, resale_meur=cng_retired * p["resale_eur"] / 1e6, take_or_pay_meur=top_cost / 1e6,
            blocked_depots=", ".join(sorted(blocked)),
        ))
        for d in DEPOTS:
            dep_rows.append(dict(scenario=name, year=y, depot=d, peak_mw=round(loads[d] / p["window_h"], 2),
                                 capacity_mw=round(capE(d, y) / p["window_h"], 2)))
    Y = pd.DataFrame(rows)
    Y["opex_meur"] = Y.opex_energy_meur + Y.opex_maint_meur
    Y["capex_over_emt_invest"] = (Y.capex_total_meur / Y.emt_invest_ref_meur).round(2)

    W = Y[Y.year <= WINDOW_END]
    disc = (1 + p["discount_rate"]) ** -(W.year - 2026)
    cash = W.capex_total_meur + W.opex_meur + W.take_or_pay_meur - W.resale_meur
    Y.attrs["fleet_value_2035_meur"] = value_2035 / 1e6
    Y.attrs["npv_meur"] = float((cash * disc).sum() - value_2035 / 1e6 * (1 + p["discount_rate"]) ** -(WINDOW_END - 2026))

    dep = pd.DataFrame([dict(scenario=name, depot=d, mw_today=round(cap_mw[d], 1) if d != "La Elipa" else 0.0,
                             need_mw_100pct=round(final_E.get(d, 0) / p["window_h"], 1),
                             upgrade_ready=upgrades.get(d, {}).get("ready"),
                             bess_mwh=round(batteries.get(d, {}).get("nameplate_mwh", 0), 1),
                             bess_unbridged_mwh=round(batteries.get(d, {}).get("unbridged_mwh", 0), 1),
                             bess_ready=batteries.get(d, {}).get("ready"))
                        for d in DEPOTS])
    return Y, dep, pd.DataFrame(dep_rows), L


def summarise(Yfull, L, p):
    hit = Yfull.loc[(Yfull.n_cng == 0) & (Yfull.lines_electric == len(L)), "year"]
    over_max_full = int(Yfull.cng_over_max_age.max())
    Y = Yfull[Yfull.year <= WINDOW_END].copy(); Y.attrs = Yfull.attrs
    last = Y.iloc[-1]
    capex = Y.capex_total_meur.sum(); opex = Y.opex_meur.sum()
    avoided = Y.co2_avoided_t.sum()
    value = Y.attrs["fleet_value_2035_meur"]
    net = capex + opex + Y.take_or_pay_meur.sum() - Y.resale_meur.sum() - value
    blocked = sorted({d for s in Y.blocked_depots for d in s.split(", ") if d})
    ref = Y.emt_invest_ref_meur
    binding = []
    if len(hit) == 0:
        if p.get("budget_cap_meur"):
            binding.append(f"budget cap EUR {p['budget_cap_meur']}M/yr")
        if Y.delivered.max() >= p["max_intake"]:
            binding.append("bus deliveries (max intake)")
        if not binding:
            binding.append("purchase pace (by design)")
        if blocked and Y.idle_ze.max() > 50:
            binding.append("depot power: " + ", ".join(blocked))
    lifecycle = Y.co2_t.sum() + Y.embodied_new_t.sum()
    return dict(
        scenario=Y.scenario.iloc[0],
        ze_100_year=int(hit.min()) if len(hit) else "after 2040",
        max_cng_over_max_age=over_max_full,
        ze_pct_2030=float(Y.loc[Y.year == 2030, "ze_share_pct"].iloc[0]),
        ze_pct_2035=float(last.ze_share_pct),
        riders_ze_2030_pct=float(Y.loc[Y.year == 2030, "riders_ze_lines_pct"].iloc[0]),
        buses_bought=int(Y.delivered.sum()), peak_intake=int(Y.delivered.max()),
        early_scrapped=int(Y.early_scrapped.sum()), max_cng_over_life=int(Y.cng_over_life.max()),
        max_idle_ze=int(Y.idle_ze.max()), buses_deferred_for_power=int(Y.deferred_for_power.sum()),
        capex_meur=round(capex), capex_buses=round(Y.capex_buses_meur.sum()),
        capex_chargers=round(Y.capex_chargers_meur.sum()), capex_grid=round(Y.capex_grid_meur.sum()),
        capex_bess=round(Y.capex_bess_meur.sum()), capex_h2=round(Y.capex_h2_meur.sum()),
        capex_battery_swaps=round(Y.capex_battery_swaps_meur.sum()), la_elipa=round(Y.capex_la_elipa_meur.sum()),
        grants=round(Y.grants_meur.sum()),
        peak_year_capex_meur=round(Y.capex_total_meur.max()),
        years_over_emt_budget=int((Y.capex_total_meur > ref).sum()),
        opex_meur=round(opex), fleet_value_2035_meur=round(value),
        net_cost_meur=round(net), npv_meur=round(Y.attrs["npv_meur"]),
        stranded_meur=round(Y.stranded_meur.sum(), 1), resale_meur=round(Y.resale_meur.sum(), 1),
        take_or_pay_meur=round(Y.take_or_pay_meur.sum(), 1),
        gas_2027_29_gwh=round(Y.loc[Y.year.between(2027, 2029), "gas_gwh"].sum()),
        co2_2035_t=int(last.co2_t), co2_avoided_kt=round(avoided / 1000),
        embodied_new_kt=round(Y.embodied_new_t.sum() / 1000, 1), embodied_wasted_kt=round(Y.embodied_wasted_t.sum() / 1000, 1),
        lifecycle_co2_kt=round(lifecycle / 1000), nox_t_10y=round(Y.nox_t.sum()),
        eur_per_t_avoided=round(capex * 1e6 / avoided) if avoided > 0 else None,
        binding=", ".join(binding) if binding else "none",
    )
