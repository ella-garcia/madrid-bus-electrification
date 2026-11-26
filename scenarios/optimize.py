"""Search many plan combinations and pick the best feasible one per budget level.

Feasible means, with the base assumptions (deliveries from 2028, at most 380 buses a year):
  - 100 % zero-emission by 2035,
  - yearly spend on buses + chargers + depot power within the budget level,
  - never more than 50 electric buses waiting for depot power,
  - no gas bus running past the maximum age (16 years).
Best = earliest 100 % year, then lowest NPV (capex + opex - resale - fleet value 2035, 3 %).
Usage: python scenarios/optimize.py
"""
import os, sys, itertools
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from assumptions import BASE                         # noqa: E402
from model import load_inputs, simulate, summarise    # noqa: E402
from run import INPUTS, OUT                          # noqa: E402
import scenarios as sc                               # noqa: E402

PACES = {f"target {y}": sc.target(y) for y in range(2030, 2036)}
PACES.update({"as fast as possible": sc.as_fast_as_possible, "replace at 12 years": sc.at_end_of_life})
POWER = {"grid": dict(power="grid"), "batteries + grid": dict(power="bess+grid"),
         "flexible grid": dict(power="grid", flexible_access=True),
         "batteries + flexible grid": dict(power="bess+grid", flexible_access=True)}
OVER = {"fast chargers": dict(over_range_tech="BEV"), "hydrogen": dict(over_range_tech="H2")}
ORDER = {"most km per bus first": dict(order="km_per_bus_desc"), "busiest lines first": dict(order="riders_desc"),
         "depot by depot": dict(order="depot_sequence", depot_sequence=["Carabanchel", "Sanchinarro", "Fuencarral", "Entrevias", "La Elipa"])}
SUPPLY = {"base (2028, 380/yr)": {}, "tender now (2027, 450/yr)": dict(first_order_delivery=2027, max_intake=450),
          "all-in now (2027, 450/yr, power ordered 2026)": dict(first_order_delivery=2027, max_intake=450, decision_year=2026)}
BUDGET = {"EMT today (EUR 167M)": 167, "EUR 200M": 200, "EUR 250M": 250, "no cap": None}
MAX_IDLE = 50

if __name__ == "__main__":
    L, fleet = load_inputs(*INPUTS)
    rows = []
    for (sn, sp), (pn, pf), (wn, wp), (on, op), (rn, rp), (bn, bv) in itertools.product(
            SUPPLY.items(), PACES.items(), POWER.items(), OVER.items(), ORDER.items(), BUDGET.items()):
        p = {**BASE, "deliveries": pf, **wp, **op, **rp, **sp, "budget_cap_meur": bv}
        Y, D, DY, Lr = simulate(p, L, fleet, "opt")
        m = summarise(Y, Lr, p)
        spend = (Y.capex_buses_meur + Y.capex_chargers_meur + Y.capex_grid_meur + Y.capex_bess_meur).max()
        rows.append(dict(supply=sn, pace=pn, power=wn, over_range=on, order=rn, budget=bn,
                         ze_100_year=m["ze_100_year"], ze_pct_2030=m["ze_pct_2030"], ze_pct_2035=m["ze_pct_2035"],
                         max_idle=m["max_idle_ze"], peak_spend_meur=round(spend), capex_meur=m["capex_meur"],
                         npv_meur=m["npv_meur"], net_cost_meur=m["net_cost_meur"], co2_avoided_kt=m["co2_avoided_kt"],
                         early_scrapped=m["early_scrapped"], embodied_wasted_kt=m["embodied_wasted_kt"],
                         riders_ze_2030_pct=m["riders_ze_2030_pct"], peak_intake=m["peak_intake"],
                         over_max_age=m["max_cng_over_max_age"]))
    R = pd.DataFrame(rows)
    R["year_num"] = pd.to_numeric(R.ze_100_year, errors="coerce")
    R["feasible"] = (R.year_num <= 2035) & (R.max_idle <= MAX_IDLE) & (R.over_max_age == 0)
    R.to_csv(os.path.join(OUT, "optimize_all.csv"), index=False)
    best = (R[R.feasible].sort_values(["supply", "budget", "year_num", "npv_meur"]).groupby(["supply", "budget"], sort=False).head(1))
    closest = (R[~R.feasible].sort_values(["supply", "budget", "ze_pct_2035", "npv_meur"], ascending=[True, True, False, True])
               .groupby(["supply", "budget"], sort=False).head(1))
    closest = closest[~closest.set_index(["supply", "budget"]).index.isin(best.set_index(["supply", "budget"]).index)]
    best = pd.concat([best, closest.assign(note="no feasible plan: closest")])
    best.to_csv(os.path.join(OUT, "optimize_best.csv"), index=False)
    pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
    print(f"{len(R)} plans run, {int(R.feasible.sum())} feasible")
    print(best.drop(columns=["year_num", "feasible"]).to_string(index=False))
