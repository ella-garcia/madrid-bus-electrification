"""Depot-by-depot roadmap to 100 % zero-emission by 2035 (local, branch research-scenario-inputs).

Rules
1. Each year EMT retires gas buses OLDEST FIRST and replaces each one with a new e-bus.
   2026-27 follow the 120 e-buses already awarded (70 + 50). From 2028 the yearly number is spread
   evenly over the years left to 2035, so orders stay steady, but a gas bus is never retired before
   it is 12 (no early scrapping). A gas bus that reaches 16 must go.
2. E-buses that turn 12 are renewed one for one at their own depot.
3. New e-buses go to ONE depot at a time, in this order: Carabanchel, Sanchinarro, La Elipa,
   Entrevias, Fuencarral (Las Tablas). A depot can take an e-bus only if it has a charging position
   (built at up to 120 a year) and enough grid power for it.
4. When a depot gets e-buses, its gas buses move out to the depots that are not yet electric,
   into the places freed by the oldest buses scrapped there. Scrapping prefers the depot being
   electrified, so buses move as little as possible.
5. La Elipa (closed) reopens in 2030 all-electric; until it is full its lines stay at the other
   four depots. Las Tablas (new, 650 places, all-electric) replaces Fuencarral from 2032; Fuencarral
   keeps its gas buses until they are replaced.

Money in constant 2025 euros, excluding VAT. Run: python scenarios/roadmap_2035.py
Outputs: scenarios/results/roadmap_2035/*.csv (see scenarios/README_2035.md).
"""
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "roadmap_2035"
YEARS = range(2026, 2036)
TARGET = 2035

# ---- Inputs ---------------------------------------------------------------------------------------
# Fleet register, 31 Dec 2025 (DATA): buses still in service by year first in service
GAS_COHORTS = {2010: 8, 2011: 59, 2012: 39, 2013: 19, 2016: 43, 2017: 231, 2018: 365, 2019: 231,
               2020: 233, 2021: 104, 2022: 304, 2023: 112}
EBUS_COHORTS = {2018: 17, 2019: 19, 2020: 32, 2021: 56, 2022: 50, 2023: 90, 2024: 115, 2025: 73}
H2 = {"Entrevias": 10}                      # DATA 10 hydrogen buses, Entrevias station
FLEET = 2210

# File 3 (team, main c3b5026): active buses and managed MW at 100 % electric (DATA/BRIEF formula)
FILE3 = {  # depot: (active buses, managed MW)
    "Carabanchel": (447, 14.59), "Fuencarral": (518, 20.07), "La Elipa": (290, 10.43),
    "Entrevias": (426, 13.49), "Sanchinarro": (353, 12.98)}
ORDER = ["Carabanchel", "Sanchinarro", "La Elipa", "Entrevias", "Fuencarral"]

A = dict(
    bus_life=12,             # A1 approved
    max_age=16,              # A1b approved
    points_per_year=120,     # depot-chargers note C1: EMT's best pace (Carabanchel 118, Sanchinarro 114)
    order_2026_27={2026: 70, 2027: 50},   # A14 approved
    charger_eur=110_000,     # A10 approved
    grid_upgrade_eur=5_000_000,   # A7 approved, per depot
    cng_book_price=291_000,  # A3 approved, straight line over 12 years
    resale_eur=10_000,       # A2 approved
    la_elipa_open=2030, la_elipa_points=318, la_elipa_mw=20.0, la_elipa_capex=134.3e6,  # A11 approved
    las_tablas_open=2032, las_tablas_places=650, las_tablas_mw=25.0, las_tablas_capex=229.45e6,  # N3 approved 26 Nov 2026 (team model cost)
    grid_ready=2029,         # N2 approved 26 Nov 2026: grid requests filed in 2026 + A6 3-year lead time
    # N1 approved 26 Nov 2026: today's e-buses by depot (EMT does not publish the split; set from charging points, x1.1)
    ebus_today={"Carabanchel": 375, "Fuencarral": 44, "Sanchinarro": 22, "Entrevias": 11, "La Elipa": 0},
    points_today={"Carabanchel": 375, "Fuencarral": 44, "Sanchinarro": 22, "Entrevias": 11, "La Elipa": 0},
)
ARTIC_SHARE = {"Carabanchel": 0.078, "Entrevias": 0.040, "Fuencarral": 0.048, "La Elipa": 0.003, "Sanchinarro": 0.0}  # DATA File 2 peak buses on articulated lines
BUS_PRICE = {d: 615_000 * (1 - s) + 800_000 * s for d, s in ARTIC_SHARE.items()}  # BRIEF prices
SPLIT = dict(  # N8-N10 approved 26 Nov 2026, our estimates: how each all-in unit cost divides
    charger_equipment=0.60,   # pantograph / charger hardware; the rest is installation works and labour
    grid_equipment=0.55,      # transformers, switchgear, cabling; the rest is civil works, engineering and labour
    labour_in_works=0.50,     # share of any works line that is labour
)
COMMITTED = {  # already contracted (WEB): (depot, year, positions, EUR)
    "Carabanchel +27 pantographs": ("Carabanchel", 2026, 27, 2.24e6),
    "Sanchinarro +114 pantographs": ("Sanchinarro", 2027, 114, 12.58e6),
}

# ---- Depot set-up ---------------------------------------------------------------------------------
scale = FLEET / sum(v[0] for v in FILE3.values())
home = {d: round(v[0] * scale) for d, v in FILE3.items()}            # physical buses per depot
home["Carabanchel"] += FLEET - sum(home.values())                    # rounding
mw_bus = {d: FILE3[d][1] / home[d] for d in FILE3}                   # MW per bus at the depot


def connection(d, y):
    if d == "Carabanchel": return 19.8
    if d == "Sanchinarro": return 8.0 if y < A["grid_ready"] else 8.0 + 5.5
    if d == "Entrevias":   return 0.9 if y < A["grid_ready"] else 14.0
    if d == "La Elipa":    return A["la_elipa_mw"] if y >= A["la_elipa_open"] else 0.0
    if d == "Fuencarral":  return 4.3 if y < A["las_tablas_open"] else A["las_tablas_mw"]


def run(a=A):
    e = dict(a["ebus_today"])
    pts = dict(a["points_today"])
    ebus_age = {d: Counter() for d in FILE3}       # e-bus cohorts per depot (renewals)
    left = Counter(EBUS_COHORTS)
    for d in ORDER:                                 # spread today's e-bus cohorts in proportion
        share = e[d] / 452
        for c, n in EBUS_COHORTS.items():
            ebus_age[d][c] = round(n * share)
    for d in ORDER:
        for c in EBUS_COHORTS:
            left[c] -= ebus_age[d][c]
    for c, n in left.items():                       # rounding remainder to Carabanchel
        ebus_age["Carabanchel"][c] += n

    def targets(e_le):
        """Buses housed at each depot: La Elipa lines not yet at La Elipa stay at the hosts."""
        hosted = home["La Elipa"] - e_le
        hosts = [d for d in ORDER if d != "La Elipa"]
        tot = sum(home[d] for d in hosts)
        t = {d: home[d] + round(hosted * home[d] / tot) for d in hosts}
        t["Carabanchel"] += hosted - sum(t[d] - home[d] for d in hosts)
        t["La Elipa"] = e_le
        return t

    # gas buses by depot and cohort, 31 Dec 2025
    t0 = targets(0)
    gas = {d: Counter() for d in ORDER}
    room = {d: t0[d] - e[d] - H2.get(d, 0) for d in ORDER}
    total_room = sum(room.values())
    for c, n in GAS_COHORTS.items():
        given = 0
        for d in ORDER[:-1]:
            k = round(n * room[d] / total_room); gas[d][c] += k; given += k
        gas[ORDER[-1]][c] += n - given
    # fix rounding so each depot's gas fits its room
    for d in ORDER:
        while sum(gas[d].values()) > room[d]:
            c = max(gas[d], key=lambda k: gas[d][k]); gas[d][c] -= 1
            short = [x for x in ORDER if sum(gas[x].values()) < room[x]][0]; gas[short][c] += 1

    rows, moves, retire_log, infra = [], [], [], []
    costs = []  # (year, depot, group, item, units, eur)

    def cost(y, d, group, item, eur, units=0):
        costs.append(dict(year=y, depot=d, group=group, item=item, units=units, eur=eur))

    def charger_cost(y, d, n, eur):
        cost(y, d, "depot", "charger equipment", eur * SPLIT["charger_equipment"], n)
        cost(y, d, "depot", "charger installation works", eur * (1 - SPLIT["charger_equipment"]))

    def grid_cost(y, d, eur, item="grid connection"):
        cost(y, d, "depot", f"{item}: equipment", eur * SPLIT["grid_equipment"])
        cost(y, d, "depot", f"{item}: civil works and engineering", eur * (1 - SPLIT["grid_equipment"]))

    def new_depot_cost(y, d, total, positions, years):
        share = 1 / years
        ch = positions * a["charger_eur"]
        charger_cost(y, d, round(positions * share), ch * share)
        grid_cost(y, d, a["grid_upgrade_eur"] * share, "new substation")
        cost(y, d, "depot", "building and civil works", (total - ch - a["grid_upgrade_eur"]) * share)
    for y in YEARS:
        # 1. infrastructure this year
        capex = Counter()
        for name, (d, yr, n, eur) in COMMITTED.items():
            if yr == y:
                pts[d] += n; capex["chargers (committed)"] += eur; infra.append((y, d, name)); charger_cost(y, d, n, eur)
        if a["grid_ready"] - 2 <= y < a["grid_ready"]:
            for d in ("Sanchinarro", "Entrevias"):
                capex["grid upgrades"] += a["grid_upgrade_eur"] / 2; grid_cost(y, d, a["grid_upgrade_eur"] / 2, "grid upgrade")
        if y == a["grid_ready"]:
            for d in ("Sanchinarro", "Entrevias"):
                infra.append((y, d, "grid upgrade in service"))
        if y == a["la_elipa_open"]:
            pts["La Elipa"] = a["la_elipa_points"]; infra.append((y, "La Elipa", f"reopens all-electric, {a['la_elipa_points']} positions"))
        if a["la_elipa_open"] - 3 <= y < a["la_elipa_open"]:
            capex["La Elipa rebuild"] += a["la_elipa_capex"] / 3; new_depot_cost(y, "La Elipa", a["la_elipa_capex"], a["la_elipa_points"], 3)
        if y == a["las_tablas_open"]:
            pts["Fuencarral"] = max(pts["Fuencarral"], a["las_tablas_places"]); infra.append((y, "Fuencarral", f"Las Tablas opens, {a['las_tablas_places']} places"))
        if a["las_tablas_open"] - 4 <= y < a["las_tablas_open"]:
            capex["Las Tablas depot"] += a["las_tablas_capex"] / 4; new_depot_cost(y, "Fuencarral", a["las_tablas_capex"], a["las_tablas_places"], 4)

        # 2. renewals of e-buses reaching 12 (same depot)
        renew = 0
        for d in ORDER:
            n = ebus_age[d].pop(y - a["bus_life"], 0)
            if n:
                ebus_age[d][y] += n; renew += n; cost(y, d, "buses", "e-buses renewing e-buses", n * BUS_PRICE[d], n)

        # 3. how many gas buses to replace
        gas_total = sum(sum(g.values()) for g in gas.values())
        forced = sum(n for g in gas.values() for c, n in g.items() if y - c >= a["max_age"])
        eligible = sum(n for g in gas.values() for c, n in g.items() if y - c >= a["bus_life"])
        if y in a["order_2026_27"]:
            want = a["order_2026_27"][y]
        else:
            # steady orders to 2035, but never scrap a gas bus younger than 12 to do it
            want = min(-(-gas_total // (TARGET - y + 1)), eligible) if a.get("no_early_scrap", True) \
                else -(-gas_total // (TARGET - y + 1))
        want = max(want, forced)

        # 4. capacity per depot: positions (built up to 120 a year), power, places
        cap = {}
        for d in ORDER:
            power = int(connection(d, y) / mw_bus[d] + 1e-9)
            build_ok = y >= {"Carabanchel": 2026, "Sanchinarro": 2028, "Entrevias": a["grid_ready"],
                             "La Elipa": a["la_elipa_open"], "Fuencarral": a["las_tablas_open"]}[d]
            reach = pts[d] + (a["points_per_year"] if build_ok and d not in ("La Elipa",) else 0)
            if d == "Fuencarral" and y < a["las_tablas_open"]:
                reach = pts[d]                                   # no new chargers at old Fuencarral
            places = home[d] - H2.get(d, 0) if d != "La Elipa" else home[d]
            cap[d] = max(0, min(reach, power, places) - e[d])

        # 5. place new e-buses depot by depot
        n_new = min(want, sum(cap.values()), gas_total)
        deferred = want - n_new
        placed = Counter(); k = n_new
        for d in ORDER:
            take = min(k, cap[d]); placed[d] = take; k -= take
        for d in ORDER:
            e[d] += placed[d]
            ebus_age[d][y] += placed[d]
            new_pts = max(0, e[d] - pts[d])
            if new_pts:
                if d not in ("La Elipa",) and not (d == "Fuencarral" and y >= a["las_tablas_open"] and pts[d] >= a["las_tablas_places"]):
                    capex["new charging positions"] += new_pts * a["charger_eur"]; charger_cost(y, d, new_pts, new_pts * a["charger_eur"])
                pts[d] += new_pts

        # 6. scrap the oldest gas buses, preferring depots that must shed gas
        t = targets(e["La Elipa"])
        allowed = {d: t[d] - e[d] - H2.get(d, 0) for d in ORDER}
        scrapped = Counter(); early = 0; writeoff = 0.0
        for _ in range(n_new):
            oldest = min(c for g in gas.values() for c, n in g.items() if n > 0)
            src = sorted([d for d in ORDER if gas[d][oldest] > 0],
                         key=lambda d: -(sum(gas[d].values()) - allowed[d]))[0]
            gas[src][oldest] -= 1; scrapped[oldest] += 1
            age = y - oldest
            if age < a["bus_life"]:
                early += 1; writeoff += a["cng_book_price"] * (a["bus_life"] - age) / a["bus_life"]
        for c, n in scrapped.items():
            retire_log.append(dict(year=y, cohort=c, age=y - c, buses=n))

        # 7. move gas buses out of depots with too many, into depots with room
        for d in ORDER:
            while sum(gas[d].values()) > allowed[d]:
                to = [x for x in ORDER if sum(gas[x].values()) < allowed[x]]
                if not to: break
                youngest = max(c for c, n in gas[d].items() if n > 0)
                gas[d][youngest] -= 1; gas[to[0]][youngest] += 1
                moves.append(dict(year=y, from_depot=d, to_depot=to[0], cohort=youngest))

        for d in ORDER:
            if placed[d]:
                cost(y, d, "buses", "e-buses replacing gas", placed[d] * BUS_PRICE[d], placed[d])
                capex["e-buses (replace gas)"] += placed[d] * BUS_PRICE[d]
        capex["e-buses (renew e-buses)"] += sum(c["eur"] for c in costs if c["year"] == y and c["item"] == "e-buses renewing e-buses")
        for d in ORDER:
            g = sum(gas[d].values())
            rows.append(dict(year=y, depot=d, buses_housed=t[d], ebuses=e[d], h2=H2.get(d, 0), gas=g,
                             positions=pts[d], mw_needed=round(e[d] * mw_bus[d], 1), mw_connection=connection(d, y),
                             electric_pct=round(100 * (e[d] + H2.get(d, 0)) / t[d], 1) if t[d] else None))
        infra_year = dict(year=y, gas_replaced=n_new, ebus_renewals=renew, buses_bought=n_new + renew,
                          deferred_for_capacity=deferred, early_scrapped=early,
                          writeoff_meur=round(writeoff / 1e6, 2),
                          oldest_gas_left=min((c for g in gas.values() for c, n in g.items() if n > 0), default=None),
                          gas_left=sum(sum(g.values()) for g in gas.values()),
                          **{f"capex_{k}": round(v / 1e6, 1) for k, v in capex.items()})
        rows_y = infra_year
        rows_y["capex_total_meur"] = round(sum(capex.values()) / 1e6, 1)
        rows.append(dict(depot="_YEAR", **rows_y))

    R = pd.DataFrame(rows)
    D = R[R.depot != "_YEAR"].drop(columns=[c for c in R.columns if c.startswith("capex") or c in
         ("gas_replaced", "ebus_renewals", "buses_bought", "deferred_for_capacity", "early_scrapped",
          "writeoff_meur", "oldest_gas_left", "gas_left")])
    Yr = R[R.depot == "_YEAR"].drop(columns=["depot", "buses_housed", "ebuses", "h2", "gas", "positions",
                                            "mw_needed", "mw_connection", "electric_pct"]).fillna(0)
    M = pd.DataFrame(moves)
    RL = pd.DataFrame(retire_log)
    return D, Yr, M, RL, pd.DataFrame(infra, columns=["year", "depot", "event"]), pd.DataFrame(costs)


def checks(D, Yr, M, RL):
    out = []
    def ok(name, cond, detail=""):
        out.append((name, "PASS" if cond else "FAIL", detail))
    last = D[D.year == TARGET]
    ok("100 % zero-emission by 2035", last.gas.sum() == 0, f"gas left {last.gas.sum()}")
    ok("fleet stays 2,210 every year", (D.groupby("year").apply(lambda g: (g.ebuses + g.h2 + g.gas).sum()) == FLEET).all())
    ok("no depot uses more power than its connection", (D.mw_needed <= D.mw_connection + 0.05).all())
    ok("every e-bus has a charging position", (D.ebuses <= D.positions).all())
    ok("no gas bus older than 16", RL.age.max() <= A["max_age"] if len(RL) else True, f"oldest retired at {RL.age.max()}")
    ok("gas buses retired oldest first", (RL.sort_values(["year", "cohort"]).groupby("year").cohort.max().shift(1).fillna(0)
                                          <= RL.groupby("year").cohort.min()).all())
    ok("purchases never above EMT's record (382)", Yr.buses_bought.max() <= 382, f"max {Yr.buses_bought.max()}")
    ok("no e-bus deferred for lack of chargers", Yr.deferred_for_capacity.sum() == 0, f"deferred {Yr.deferred_for_capacity.sum()}")
    return pd.DataFrame(out, columns=["check", "result", "detail"])


if __name__ == "__main__":
    D, Yr, M, RL, I, K = run()
    OUT.mkdir(parents=True, exist_ok=True)
    K.to_csv(OUT / "costs_by_depot.csv", index=False)
    D.to_csv(OUT / "depots_by_year.csv", index=False); Yr.to_csv(OUT / "years.csv", index=False)
    M.to_csv(OUT / "moves.csv", index=False); RL.to_csv(OUT / "retirements.csv", index=False); I.to_csv(OUT / "infrastructure.csv", index=False)
    C = checks(D, Yr, M, RL); C.to_csv(OUT / "checks.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(Yr.to_string(index=False)); print()
    print(D.pivot(index="year", columns="depot", values="electric_pct").to_string()); print()
    print(D.pivot(index="year", columns="depot", values="ebuses").to_string()); print()
    print(D.pivot(index="year", columns="depot", values="gas").to_string()); print()
    if len(M):
        print(M.groupby(["year", "from_depot", "to_depot"]).size().rename("buses moved").reset_index().to_string(index=False)); print()
    print(RL.pivot_table(index="year", columns="cohort", values="buses", aggfunc="sum").fillna(0).astype(int).to_string()); print()
    print(I.to_string(index=False)); print()
    print(C.to_string(index=False))
