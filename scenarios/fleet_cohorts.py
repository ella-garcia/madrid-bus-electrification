"""Gas and electric buses in service on 31 Dec 2025, by year first in service (EMT fleet register).

This is the evidence behind the 2035 recommendation: the youngest gas buses (bought in 2023)
turn 12 in 2035, so 2035 is the first year Madrid can reach 100 % zero-emission without
scrapping a gas bus before the end of its 12-year life.

Input:  data_raw/emt_fleet_history.csv (EMT open data, datos.madrid.es dataset 300241)
Run:    python scenarios/fleet_cohorts.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BUS_LIFE = 12          # A1 approved: median retirement age in the register
BASELINE = "2025-12-31"


def cohorts(path=ROOT / "data_raw" / "emt_fleet_history.csv"):
    f = pd.read_csv(path, dtype=str).apply(lambda c: c.str.strip()).drop_duplicates()
    last = f.sort_values(["vehicleId", "dateIni"]).groupby("vehicleId").tail(1)   # latest record per bus
    first = f.groupby("vehicleId").dateIni.min()                                    # first day in service
    active = last[last.dateEnd.isna() | (last.dateEnd >= BASELINE)]                 # still in service at baseline
    year = active.vehicleId.map(first).str[:4].astype(int)
    table = pd.crosstab(year, active.fuelType).rename(columns={"GN": "gas", "EL": "electric", "H": "hydrogen"})
    return table


if __name__ == "__main__":
    t = cohorts()
    t["turns_12_in"] = t.index + BUS_LIFE
    t["turns_13_in"] = t.index + BUS_LIFE + 1
    print(t.to_string())
    print("\nTotals:", t[["gas", "electric", "hydrogen"]].sum().to_dict())
    last_gas = t[t.gas > 0].index.max()
    print(f"Youngest gas buses: {int(t.loc[last_gas, 'gas'])} bought in {last_gas}, turn {BUS_LIFE} in {last_gas + BUS_LIFE}")
    # Buses entering service per year (all fuels): EMT's delivery record
    f = pd.read_csv(ROOT / "data_raw" / "emt_fleet_history.csv", dtype=str).apply(lambda c: c.str.strip()).drop_duplicates()
    intake = f.groupby("vehicleId").dateIni.min().str[:4].astype(int).value_counts().sort_index()
    print("\nBuses entering service per year (record):", intake.loc[2015:].to_dict())
