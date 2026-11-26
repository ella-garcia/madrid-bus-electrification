"""Financial plan to 2035: who pays, year by year (Projection 4 of the storyline document).

Funding stack, with the finance assumptions approved on 26 Nov 2026:
  - EMT own funds:   EUR 35M a year (team financial model, EMT 2026 budget)
  - EU grants:       20 % of bus capex (team value, so both models compare)
  - CAE certificates: EUR 10M a year in 2030-35, EUR 60M in total (our estimate; bus eligibility to confirm)
  - Borrowing:       the rest, at 3.2 % (Comunidad de Madrid green bonds), repaid over 15 years
  - Running-cost savings = energy + maintenance against 2026 (our model's opex)

Source plans:
  --plan d4       (default) our scenario model, plan "D4 Best 2035" (results/years.csv), as in the document
  --plan roadmap  the depot-by-depot roadmap (results/roadmap_2035/), which adds Las Tablas
Run:  python scenarios/funding_2035.py [--plan d4|roadmap]
"""
import argparse
from pathlib import Path
import pandas as pd

RES = Path(__file__).resolve().parent / "results"
OWN_FUNDS = 35.0
GRANT_SHARE = 0.20
CAE = {y: 10.0 for y in range(2030, 2036)}
RATE = 0.032
REPAY_YEARS = 15


def load(plan):
    if plan == "d4":
        Y = pd.read_csv(RES / "years.csv")
        y = Y[(Y.scenario == "D4 Best 2035") & (Y.year <= 2035)]
        return pd.DataFrame(dict(year=y.year.values, capex=y.capex_total_meur.values,
                                 bus_capex=y.capex_buses_meur.values, opex=y.opex_meur.values))
    K = pd.read_csv(RES / "roadmap_2035" / "costs_by_depot.csv")
    tot = K.groupby("year").eur.sum() / 1e6
    bus = K[K.group == "buses"].groupby("year").eur.sum().reindex(tot.index, fill_value=0) / 1e6
    return pd.DataFrame(dict(year=tot.index, capex=tot.values, bus_capex=bus.values, opex=float("nan")))


def funding(df):
    rows, outstanding, draws = [], 0.0, []
    opex0 = df.opex.iloc[0]
    for r in df.itertuples():
        grants = GRANT_SHARE * r.bus_capex
        cae = CAE.get(r.year, 0.0)
        borrow = max(0.0, r.capex - grants - OWN_FUNDS - cae)
        repay = sum(d / REPAY_YEARS for (yy, d) in draws if r.year > yy and r.year - yy <= REPAY_YEARS)
        interest = RATE * outstanding               # on the balance at the start of the year
        outstanding += borrow - repay
        draws.append((r.year, borrow))
        rows.append(dict(year=r.year, investment=r.capex, eu_grants=grants, own_funds=OWN_FUNDS, cae=cae,
                         new_borrowing=borrow, repayment=repay, interest=interest, debt_end_year=outstanding,
                         running_cost_saving=opex0 - r.opex if pd.notna(r.opex) else float("nan")))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", choices=["d4", "roadmap"], default="d4")
    F = funding(load(ap.parse_args().plan))
    pd.set_option("display.width", 200)
    print(F.round(1).to_string(index=False))
    t = F.sum(numeric_only=True)
    print(f"\nTotals 2026-35: investment {t.investment:,.0f} | grants {t.eu_grants:,.0f} | own funds {t.own_funds:,.0f} "
          f"| CAE {t.cae:,.0f} | borrowing {t.new_borrowing:,.0f} | interest {t.interest:,.0f} "
          f"| peak borrowing {F.new_borrowing.max():,.0f} in {int(F.loc[F.new_borrowing.idxmax(), 'year'])}  (EUR M)")
