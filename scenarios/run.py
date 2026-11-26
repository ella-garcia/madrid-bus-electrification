"""Run every scenario and write results to scenarios/results/. Usage: python scenarios/run.py"""
import os, sys, json
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from assumptions import BASE, LABELS          # noqa: E402
from model import load_inputs, simulate, summarise  # noqa: E402
from scenarios import SCENARIOS               # noqa: E402

ROOT = os.path.dirname(HERE); RAW = os.path.join(ROOT, "data_raw")
INPUTS = (os.path.join(HERE, "inputs", "line_table_handoff.csv"), os.path.join(RAW, "emt_fleet_history.csv"),
          os.path.join(RAW, "emt_ridership_2026.csv"), os.path.join(RAW, "emt_calendar.csv"))
OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
META = ("name", "note", "group")


def params(s):
    return {**BASE, **{k: v for k, v in s.items() if k not in META}}


if __name__ == "__main__":
    L, fleet = load_inputs(*INPUTS)
    years, depots, dyears, summary, lines = [], [], [], [], []
    for s in SCENARIOS:
        p = params(s)
        Y, D, DY, Lr = simulate(p, L, fleet, s["name"])
        years.append(Y); depots.append(D); dyears.append(DY)
        summary.append({"group": s["group"], **summarise(Y, Lr, p), "note": s["note"]})
        lines.append(Lr.assign(scenario=s["name"])[["scenario", "line_label", "depot_name", "tech_now", "year_converted"]])
    pd.concat(years).to_csv(os.path.join(OUT, "years.csv"), index=False)
    pd.concat(depots).to_csv(os.path.join(OUT, "depots.csv"), index=False)
    pd.concat(dyears).to_csv(os.path.join(OUT, "depot_years.csv"), index=False)
    S = pd.DataFrame(summary); S.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    pd.concat(lines).to_csv(os.path.join(OUT, "line_conversion.csv"), index=False)
    json.dump(LABELS, open(os.path.join(OUT, "assumptions.json"), "w"), indent=1)
    pd.set_option("display.width", 300); pd.set_option("display.max_columns", 60)
    print(S[["scenario", "ze_100_year", "ze_pct_2030", "peak_intake", "early_scrapped", "max_idle_ze", "capex_meur",
             "peak_year_capex_meur", "years_over_emt_budget", "opex_meur", "net_cost_meur", "npv_meur",
             "co2_avoided_kt", "embodied_wasted_kt", "riders_ze_2030_pct", "binding"]].to_string(index=False))
