"""One lever at a time on the recommended plan and the brief's 2030 scenario. Usage: python scenarios/sensitivity.py"""
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from assumptions import BASE                         # noqa: E402
from model import load_inputs, simulate, summarise    # noqa: E402
from run import INPUTS, OUT, params                  # noqa: E402
from scenarios import SCENARIOS                      # noqa: E402

pick = {s["name"]: s for s in SCENARIOS}
LEVERS = [
    ("base", {}),
    ("Battery takes 2 years (A16)", dict(bess_lead_years=2)),
    ("Grid upgrade 4 years (A6)", dict(grid_lead_years=4)),
    ("Max intake 300 a year (A4)", dict(max_intake=300)),
    ("Orders deliver from 2027 + 450/yr (A14)", dict(first_order_delivery=2027, max_intake=450)),
    ("La Elipa opens 2032 (A11)", dict(la_elipa_open=2032)),
    ("Bus life 14 years (A1)", dict(bus_life=14)),
    ("Electricity EUR 110/MWh (A21)", dict(elec_price_eur_mwh=110)),
    ("Electricity EUR 60/MWh (A21)", dict(elec_price_eur_mwh=60)),
    ("Maintenance gap halved (A22)", dict(maint_eur_km={"CNG": 0.19, "BEV": 0.14, "H2": 0.19})),
    ("Battery EUR 400/kWh (A8)", dict(bess_eur_kwh=400)),
    ("Grid upgrade EUR 13M per depot (A7)", dict(grid_upgrade_eur=13_000_000, flexible_access=False)),
    ("EU grants 30 % on infrastructure (A29)", dict(grant_share_infra=0.3)),
    ("Gas take-or-pay 80 % (A5)", dict(gas_take_or_pay=0.8)),
    ("Grid CO2 falls to 40 g/kWh by 2035 (A13)", dict(grid_gco2_kwh=74.0)),
    ("Discount rate 5 % (A26)", dict(discount_rate=0.05)),
    ("Budget cap EUR 200M (A27)", dict(budget_cap_meur=200)),
]
L, fleet = load_inputs(*INPUTS)
rows = []
for scen in ["D2 Best 2033 (recommended)", "B2 2030, batteries + grid"]:
    for label, over in LEVERS:
        p = {**params(pick[scen]), **over}
        Y, D, DY, Lr = simulate(p, L, fleet, scen)
        m = summarise(Y, Lr, p)
        rows.append(dict(scenario=scen, lever=label, ze_100_year=m["ze_100_year"], ze_pct_2030=m["ze_pct_2030"],
                         peak_year_capex_meur=m["peak_year_capex_meur"], npv_meur=m["npv_meur"],
                         early_scrapped=m["early_scrapped"], max_idle_ze=m["max_idle_ze"],
                         co2_avoided_kt=m["co2_avoided_kt"], take_or_pay_meur=m["take_or_pay_meur"], binding=m["binding"]))
S = pd.DataFrame(rows)
S.to_csv(os.path.join(OUT, "sensitivity.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
print(S.to_string(index=False))
