"""Consistency checks on every scenario-year. Usage: python scenarios/checks.py (after run.py)"""
import os
import numpy as np, pandas as pd
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
Y = pd.read_csv(os.path.join(R, "years.csv")); S = pd.read_csv(os.path.join(R, "summary.csv"))
res = []
def chk(name, ok, detail=""):
    res.append(bool(ok)); print(f"CHECK {'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))
chk("Fleet identity n_bev + n_h2 + n_cng = fleet_total", (Y.n_bev + Y.n_h2 + Y.n_cng == Y.fleet_total).all())
chk("ze_share_pct = 100 x (n_bev + n_h2) / fleet_total", np.allclose(Y.ze_share_pct, (100 * Y.n_ze / Y.fleet_total).round(1), atol=0.051))
chk("Gas buses never increase", (Y.groupby("scenario").n_cng.diff().fillna(0) <= 0).all())
chk("Electric lines never decrease", (Y.groupby("scenario").lines_electric.diff().fillna(0) >= 0).all())
chk("Deliveries never above 450 a year", Y.delivered.max() <= 450, f"max {Y.delivered.max()}")
chk("2026 deliveries = the 70 already ordered", (Y[Y.year == 2026].delivered == 70).all())
parts = [c for c in Y if c.startswith("capex_") and c not in ("capex_total_meur", "capex_over_emt_invest")]
chk("Capex total = sum of its parts - grants", np.allclose(Y.capex_total_meur, Y[parts].sum(axis=1) - Y.grants_meur))
chk("Fleet never below 2,210 buses (no service cut)", (Y.fleet_total >= 2210).all(), f"min {Y.fleet_total.min()}")
nc4 = Y[~Y.scenario.str.startswith("C4")]
chk("No more than 25 buses idle in any year, except C4 (batteries only, fails by design)", nc4.idle_ze.max() <= 25, f"max {nc4.idle_ze.max()}")
om = S.set_index("scenario").max_cng_over_max_age
chk("No gas bus past 16 years, except C4 (batteries only, fails by design)", (om.drop([s for s in om.index if s.startswith("C4")]) <= 1).all(), om[om > 0].to_dict())
chk("A year at 100 % emits electricity CO2 only (18-20 kt)", Y[Y.ze_share_pct == 100].co2_t.between(18000, 20000).all())
chk("Running costs 2035 below 2026 in every scenario",
    (Y[Y.year == 2035].set_index("scenario").opex_meur < Y[Y.year == 2026].set_index("scenario").opex_meur).all())
w = Y[Y.year <= 2035]
chk("Buses bought 2026-35 >= gas buses (1,748) in every plan that reaches 100 % by 2035",
    all(w[w.scenario == r.scenario].delivered.sum() >= 1748 for r in S.itertuples() if str(r.ze_100_year).isdigit() and int(r.ze_100_year) <= 2035))
chk("2026 gas use ~ 600-650 GWh vs tender 583 GWh/yr", Y[Y.year == 2026].gas_gwh.between(590, 660).all())
print(f"\n{sum(res)} PASS / {len(res) - sum(res)} FAIL")
