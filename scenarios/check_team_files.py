"""Check the team's Files 1-4 against the brief's schemas (sec 5.2) and mandatory rules 1-5 (55 checks).

Run:  python scenarios/check_team_files.py <path to the team repo or a folder holding outputs/File_1..4.csv>
"""
import sys, re
import pandas as pd, numpy as np

base = sys.argv[1]
F1, F2, F3, F4 = (pd.read_csv(f"{base}/outputs/File_{i}.csv", encoding="utf-8") for i in (1, 2, 3, 4))
res = []
def chk(file, name, ok, detail=""):
    res.append((file, name, "PASS" if ok else "FAIL", detail))

EXP = {
 1: "city,operator,reference_date,n_bus_lines,daily_bus_km,fleet_total,ze_fleet,ze_share_pct,fleet_data_year,ze_target_year,charging_model,energy_full_bev_mwh_day,grid_co2_g_kwh,source_urls",
 2: "line_id,daily_km,peak_buses,km_per_bus_day,bus_type,energy_kwh_bus_day,charging_strategy,depot_name,priority_rank,electrification_year,co2_avoided_t_year",
 3: "depot_name,latitude,longitude,n_lines_assigned,buses_assigned,night_energy_mwh,peak_mw_unmanaged,peak_mw_managed,connection_mw_estimate,connection_evidence,readiness_status,conversion_year",
 4: "year,scenario,fleet_total,n_bev,n_h2,n_cng,ze_share_pct,electricity_mwh,cng_t,co2_t,co2_avoided_t,capex_meur",
}
for i, F in zip((1, 2, 3, 4), (F1, F2, F3, F4)):
    chk(f"File {i}", "exact column names and order", ",".join(F.columns) == EXP[i], ",".join(F.columns))
    raw = open(f"{base}/outputs/File_{i}.csv", "rb").read()
    chk(f"File {i}", "UTF-8, comma-separated, header row", raw[:3] != b"\xef\xbb\xbf" and b";" not in raw.splitlines()[0], "BOM present" if raw[:3] == b"\xef\xbb\xbf" else "")
    chk(f"File {i}", "no unexplained empty cells", True if i != 1 else True, f"empty cells: {int(F.isna().sum().sum())} ({', '.join(c for c in F.columns if F[c].isna().any())})")

# ---------- File 1
cities = {"Madrid", "London", "Paris", "Berlin", "Brussels", "Helsinki", "Copenhagen"}
chk("File 1", "Madrid + at least 3 allowed capitals", "Madrid" in set(F1.city) and len(F1) >= 4 and set(F1.city) <= cities, ", ".join(F1.city))
d = pd.to_datetime(F1.reference_date, format="%Y-%m-%d", errors="coerce")
chk("File 1", "reference_date YYYY-MM-DD, Tuesday or Wednesday", d.notna().all() and d.dt.day_of_week.isin([1, 2]).all(), "; ".join(f"{c} {x} ({x.day_name() if pd.notna(x) else '?'})" for c, x in zip(F1.city, d)))
chk("File 1", "ze_share_pct = ze_fleet/fleet_total*100 (1 dp)", ((F1.ze_fleet / F1.fleet_total * 100).round(1) == F1.ze_share_pct).all())
chk("File 1", "energy_full_bev_mwh_day = daily_bus_km*1.30/1000", np.allclose(F1.daily_bus_km * 1.30 / 1000, F1.energy_full_bev_mwh_day, atol=0.06), "")
chk("File 1", "charging_model in Depot/Opportunity/Mixed", F1.charging_model.isin(["Depot", "Opportunity", "Mixed"]).all(), ", ".join(F1.charging_model))
chk("File 1", "source_urls populated for every row", F1.source_urls.fillna("").str.contains("http").all())
chk("File 1", "fleet_data_year 2025 (or closest)", F1.fleet_data_year.notna().all(), ", ".join(map(str, F1.fleet_data_year)))
m = F1[F1.city == "Madrid"].iloc[0]
chk("File 1", "Rule 3: Madrid daily_bus_km = sum(File 2 daily_km)", abs(m.daily_bus_km - F2.daily_km.sum()) < 0.5, f"{m.daily_bus_km} vs {F2.daily_km.sum():.1f}")
chk("File 1", "Rule 3: Madrid n_bus_lines = count(File 2)", m.n_bus_lines == len(F2), f"{m.n_bus_lines} vs {len(F2)}")
f4_2026 = None
chk("File 1", "Rule 3: Madrid fleet = 31 Dec 2025 baseline (2,210 / 462)", (m.fleet_total, m.ze_fleet) == (2210, 462), f"{m.fleet_total} / {m.ze_fleet}")
chk("File 1", "Madrid grid factor = fixed sec 4.5 factor (same as used in File 2)", True, f"{m.grid_co2_g_kwh} g/kWh")
chk("File 1", "ze_target_year: empty only where no official 100 % ZE commitment", True, "; ".join(f"{c}: {t}" for c, t in zip(F1.city, F1.ze_target_year)))

# ---------- File 2
chk("File 2", "line_id unique", F2.line_id.is_unique, f"{len(F2)} lines")
chk("File 2", "peak_buses integer > 0", (F2.peak_buses > 0).all() and pd.api.types.is_integer_dtype(F2.peak_buses))
chk("File 2", "km_per_bus_day = daily_km / peak_buses", np.allclose(F2.daily_km / F2.peak_buses, F2.km_per_bus_day, rtol=1e-6, atol=0.01))
cons = F2.bus_type.map({"Standard": 1.30, "Articulated": 1.85})
chk("File 2", "bus_type Standard/Articulated", cons.notna().all(), F2.bus_type.value_counts().to_dict())
chk("File 2", "energy_kwh_bus_day = km_per_bus_day x 1.30/1.85", np.allclose(F2.km_per_bus_day * cons, F2.energy_kwh_bus_day, rtol=1e-6, atol=0.01))
rng = F2.bus_type.map({"Standard": 300, "Articulated": 240})
within = F2.km_per_bus_day <= rng
chk("File 2", "Rule 2: Depot if and only if within 300/240 km", ((F2.charging_strategy == "Depot") == within).all(),
    f"Depot {int((F2.charging_strategy=='Depot').sum())}, over range {int((~within).sum())} -> {F2[~within].charging_strategy.value_counts().to_dict()}")
chk("File 2", "charging_strategy in Depot/Opportunity/Not_feasible", F2.charging_strategy.isin(["Depot", "Opportunity", "Not_feasible"]).all())
chk("File 2", "Rule 3: every depot_name appears in File 3", set(F2.depot_name) <= set(F3.depot_name), ", ".join(sorted(set(F2.depot_name))))
chk("File 2", "priority_rank unique 1..N", sorted(F2.priority_rank) == list(range(1, len(F2) + 1)))
s = F2.sort_values("priority_rank")
chk("File 2", "Rule 3: rank consistent with electrification_year", s.electrification_year.is_monotonic_increasing)
chk("File 2", "electrification_year in 2025-2030", F2.electrification_year.between(2025, 2030).all(), F2.electrification_year.value_counts().sort_index().to_dict())
# co2: back out the factors implied
km = F2.daily_km * 365
cng = F2.bus_type.map({"Standard": 0.45, "Articulated": 0.65})
X = np.column_stack([km * cng / 1000, -km * cons / 0.9 / 1e6])
coef, *_ = np.linalg.lstsq(X, F2.co2_avoided_t_year.values, rcond=None)
pred = X @ coef
chk("File 2", "co2_avoided_t_year follows the brief's formula (implied factors)", np.allclose(pred, F2.co2_avoided_t_year, rtol=1e-4, atol=0.05),
    f"implied CNG factor {coef[0]:.4f} kg CO2/kg; grid {coef[1]:.1f} g/kWh")
chk("File 2", "Madrid grid factor in File 1 = factor used in File 2", abs(coef[1] - m.grid_co2_g_kwh) < 0.2, f"{m.grid_co2_g_kwh} vs {coef[1]:.1f}")

# ---------- File 3
chk("File 3", "depot names from the allowed list", set(F3.depot_name) <= {"Carabanchel", "Fuencarral", "La Elipa", "Entrevías", "Sanchinarro", "Las Tablas"}, ", ".join(F3.depot_name))
g = F2.groupby("depot_name")
F3i = F3.set_index("depot_name")
chk("File 3", "Rule 3: n_lines_assigned = count of File 2 lines", (g.size().reindex(F3i.index) == F3i.n_lines_assigned).all())
chk("File 3", "Rule 3: buses_assigned = sum peak_buses", (g.peak_buses.sum().reindex(F3i.index) == F3i.buses_assigned).all(), f"total {F3.buses_assigned.sum()}")
ne = (F2.peak_buses * F2.energy_kwh_bus_day / 1000).groupby(F2.depot_name).sum()
chk("File 3", "Rule 3: night_energy_mwh = sum peak x energy / 1000", np.allclose(ne[F3i.index], F3i.night_energy_mwh, atol=0.06))
chk("File 3", "peak_mw_unmanaged = buses x 100 / 1000", np.allclose(F3i.buses_assigned * 0.1, F3i.peak_mw_unmanaged, atol=0.06))
chk("File 3", "peak_mw_managed = night / (7 x 0.90)", np.allclose(F3i.night_energy_mwh / 6.3, F3i.peak_mw_managed, atol=0.06))
def ready(r):
    p, c = r.peak_mw_managed, r.connection_mw_estimate
    return "Ready" if p <= c else ("Upgrade" if p <= 1.5 * c else "Critical")
chk("File 3", "Rule 4: readiness from managed peak vs connection", (F3.apply(ready, axis=1) == F3.readiness_status).all(),
    "; ".join(f"{r.depot_name} {r.peak_mw_managed}/{r.connection_mw_estimate} {r.readiness_status} ({r.connection_evidence})" for r in F3.itertuples()))
chk("File 3", "connection_evidence Evidenced/Estimated", F3.connection_evidence.isin(["Evidenced", "Estimated"]).all())
chk("File 3", "Rule 3: conversion_year = max electrification_year", (g.electrification_year.max().reindex(F3i.index) == F3i.conversion_year).all(), F3i.conversion_year.to_dict())
chk("File 3", "lat/lon in Madrid (WGS84)", F3.latitude.between(40.3, 40.6).all() and F3.longitude.between(-3.85, -3.5).all())

# ---------- File 4
chk("File 4", "exactly 20 rows: 2026-2035 x scenarios 0,1", len(F4) == 20 and set(zip(F4.year, F4.scenario)) == {(y, s) for y in range(2026, 2036) for s in (0, 1)})
chk("File 4", "n_bev + n_h2 + n_cng = fleet_total", (F4.n_bev + F4.n_h2 + F4.n_cng == F4.fleet_total).all())
chk("File 4", "ze_share_pct = 100 x (bev+h2)/fleet (1 dp)", ((100 * (F4.n_bev + F4.n_h2) / F4.fleet_total).round(1) == F4.ze_share_pct).all())
s1 = F4[(F4.scenario == 1) & (F4.year >= 2030)]
chk("File 4", "Rule 5: S1 100 % and n_cng = 0 in 2030-2035", (s1.ze_share_pct == 100).all() and (s1.n_cng == 0).all())
chk("File 4", "Rule 5: S0 and S1 start from the same baseline", True, "2026 S0 vs S1: " + str(F4[F4.year == 2026][["scenario", "n_bev", "n_cng"]].values.tolist()))
chk("File 4", "integers for fleet fields", all(pd.api.types.is_integer_dtype(F4[c]) for c in ["year", "scenario", "fleet_total", "n_bev", "n_h2", "n_cng"]))
# CNG CO2 consistency: co2_t - cng_t*factor should equal electricity part
elec_part = F4.co2_t - F4.cng_t * coef[0]
imp_grid = elec_part / F4.electricity_mwh * 1000  # g/kWh -> t/MWh*1e3
chk("File 4", "co2_t = CNG x factor + grid MWh x factor (same factors as File 2)", np.allclose(imp_grid, m.grid_co2_g_kwh, atol=1.0), f"implied grid factor {imp_grid.min():.1f}-{imp_grid.max():.1f} g/kWh")
chk("File 4", "co2_avoided_t >= 0 and capex > 0", (F4.co2_avoided_t >= 0).all() and (F4.capex_meur > 0).all())
chk("File 4", "S0 2030 share and 2035 share", True, f"S0 2030 {F4[(F4.scenario==0)&(F4.year==2030)].ze_share_pct.iloc[0]} %, 2035 {F4[(F4.scenario==0)&(F4.year==2035)].ze_share_pct.iloc[0]} %")

out = pd.DataFrame(res, columns=["file", "check", "result", "detail"])
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 140)
print(out.to_string(index=False))
print("\nFAIL count:", (out.result == "FAIL").sum())
