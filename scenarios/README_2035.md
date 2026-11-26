# Code behind the 2035 recommendation

Local branch `research-scenario-inputs`. Python 3.12 with `pandas`, `numpy` and `tabulate` (`pip install pandas numpy tabulate`).
Run every command from the repository root.

## Which script makes which result

| Step | Script | What it does | Outputs | Key results |
|---|---|---|---|---|
| 1 | `scenarios/fleet_cohorts.py` | Gas and electric buses in service at 31 Dec 2025, by year first in service, and buses entering service each year (EMT fleet register) | printed | The youngest gas buses (112, bought 2023) turn 12 in **2035**. EMT's record intake is **382 (2018)**, not 159 |
| 2 | `scenarios/run.py` (uses `model.py`, `assumptions.py`, `scenarios.py`) | Our line-and-depot scenario model: 2030, 2033, 2035 plans and more, with the approved assumptions A1–A31 | `scenarios/results/summary.csv`, `years.csv` | Plan **D4 Best 2035**: 100 % in 2035, 9 young buses scrapped, €1,611M. Plan D2 (2033): 1,394 scrapped |
| 3 | `scenarios/roadmap_2035.py` | **Depot-by-depot roadmap to 2035**: retires the oldest gas buses first (never before 12), converts one depot at a time, moves gas buses out of converted depots, checks power and chargers each year. Assumptions N1–N10 approved 26 Nov 2026 | `scenarios/results/roadmap_2035/` (`depots_by_year`, `years`, `moves`, `retirements`, `infrastructure`, `costs_by_depot`, `checks`) | 100 % in 2035, **0** young buses scrapped, 2,012 e-buses, **€1,724M**, peak €260M (2029), 409 bus moves; 8 checks PASS |
| 4 | `scenarios/roadmap_2035_breakdown.py` | Cost of each depot by year: buses, chargers (equipment, installation), grid (equipment, works), building, labour estimate | `scenarios/results/roadmap_2035/breakdown.md` | Carabanchel €219M, Sanchinarro €276M, La Elipa €328M, Entrevías €332M, Fuencarral/Las Tablas €570M |
| 5 | `scenarios/funding_2035.py` | Who pays each year: own funds €35M, EU grants 20 % of buses, CAE €10M a year 2030–35, borrowing at 3.2 % over 15 years | printed | D4: borrowing **€950M**, peak €147M. Roadmap (`--plan roadmap`, with Las Tablas): €1,064M, peak €197M |
| 6 | `scenarios/blackout_backup.py` | Extra, not in the totals: batteries and solar to keep part of the fleet charging in a blackout | printed | 25 % of service: 158 MWh, about **€44M**; 5 MWp of solar €4.5–6.5M, pays back in 6–9 years |
| 7 | `scenarios/check_team_files.py <team repo>` | Checks the team's Files 1–4 against the brief's schemas and mandatory rules 1–5 | printed | 55 checks, 0 FAIL on main c3b5026 |

Run in this order:

```
python scenarios/fleet_cohorts.py
python scenarios/run.py
python scenarios/roadmap_2035.py
python scenarios/roadmap_2035_breakdown.py
python scenarios/funding_2035.py
python scenarios/funding_2035.py --plan roadmap
python scenarios/blackout_backup.py
python scenarios/check_team_files.py <path to the team repository>
```

`fleet_cohorts.py` needs `data_raw/emt_fleet_history.csv` (EMT open data, datos.madrid.es dataset 300241).

## Where the assumptions are
- A1–A31 (scenario model): `scenarios/assumptions.py`, explained in `notes/scenario-model-explained.md`.
- N1–N10 (roadmap): top of `scenarios/roadmap_2035.py`, explained in `notes/roadmap-2035.md`.
- Finance (approved 26 Nov 2026): top of `scenarios/funding_2035.py`.
- Every assumption with its source: the roadmap document's assumptions register.

## Related documents
- Storyline and the four projections (2030, 2033, 2035, financial plan): https://claude.ai/artifact/37mrrMdQKfDp6JhSYLBx9B
- Depot-by-depot roadmap to 2035: https://claude.ai/artifact/U8JuCLyVVjSAo9AqGbjPYc
- What the academic papers say: https://claude.ai/artifact/Ji3Hppo9G1Eg8mHNmuKis7
