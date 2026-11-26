"""Extra (not in the roadmap totals): batteries and solar at the depots to keep part of the
electric fleet charging during a blackout.

Inputs
  - Battery energy per bus-day: File 3 night_energy_mwh summed over the 5 depots (team main c3b5026),
    divided by the 2,200 battery-electric buses of 2035.
  - Charging efficiency 90 % (brief).
  - Battery EUR 250/kWh turnkey (A8), 90 % usable and 88 % round trip (A9).
  - Equipment to run a depot cut off from the grid: +12 % (our estimate).
  - Solar: about 1 MWp per depot, EUR 900-1,300 per kWp, about 1,650 kWh per kWp a year in Madrid
    (4.5 kWh/kWp a day on average, 2.6 in winter), electricity EUR 85/MWh (A21). Estimates to verify.
Run:  python scenarios/blackout_backup.py
"""
import pandas as pd

FILE3_NIGHT_MWH = {"Carabanchel": 91.93, "Fuencarral": 126.43, "La Elipa": 65.73,
                   "Entrevias": 85.00, "Sanchinarro": 81.77}
BEV_2035 = 2200
CHARGE_EFF = 0.90
BATT_EUR_KWH, USABLE, ROUND_TRIP = 250, 0.90, 0.88
ISLANDING = 0.12
PV_MWP, PV_EUR_KWP = 5, (900, 1300)
PV_YIELD_YEAR, PV_DAY_AVG, PV_DAY_WINTER = 1650, 4.5, 2.6
ELEC_EUR_MWH = 85


def battery_options(shares=(0.10, 0.25, 0.50)):
    per_bus_kwh = sum(FILE3_NIGHT_MWH.values()) / BEV_2035 * 1000
    rows = []
    for s in shares:
        buses = round(BEV_2035 * s)
        at_charger_mwh = buses * per_bus_kwh / 1000 / CHARGE_EFF
        nameplate = at_charger_mwh / (USABLE * ROUND_TRIP)
        cost = nameplate * BATT_EUR_KWH / 1000
        rows.append(dict(service=f"{int(s * 100)} %", buses=buses, battery_mwh=round(nameplate),
                         battery_meur=round(cost, 1), islanding_meur=round(cost * ISLANDING, 1),
                         total_meur=round(cost * (1 + ISLANDING), 1)))
    return per_bus_kwh, pd.DataFrame(rows)


def solar(per_bus_kwh):
    yr = PV_MWP * PV_YIELD_YEAR
    out = []
    for p in PV_EUR_KWP:
        capex = PV_MWP * p / 1000
        saving = yr * ELEC_EUR_MWH / 1e6
        out.append(dict(eur_per_kwp=p, capex_meur=capex, mwh_year=yr,
                        buses_a_day_avg=round(PV_MWP * PV_DAY_AVG * CHARGE_EFF / per_bus_kwh * 1000),
                        buses_a_day_winter=round(PV_MWP * PV_DAY_WINTER * CHARGE_EFF / per_bus_kwh * 1000),
                        saving_meur_year=round(saving, 2), payback_years=round(capex / saving, 1)))
    return pd.DataFrame(out)


if __name__ == "__main__":
    per_bus, B = battery_options()
    print(f"Battery energy per bus-day: {per_bus:.0f} kWh\n")
    print(B.to_string(index=False)); print()
    print(solar(per_bus).to_string(index=False))
