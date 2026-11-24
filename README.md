# Madrid bus electrification — IE Sustainability Datathon (Kearney)

Team repository for the IE × Kearney datathon on EMT Madrid's transition to a zero-tailpipe-emission bus fleet.
The model connects three levels — **line → depot → city** — and benchmarks Madrid against European capitals.

**Submission:** 27 Nov 2026, 12:00 (to confirm with organisers), by one team member through the Final Submission Form.

## What we submit

| # | Deliverable | Produced by |
|---|---|---|
| 1 | Executed Colab notebooks (`.ipynb`, all outputs visible) | `notebooks/` |
| 2 | `File_1.csv` benchmark · `File_2.csv` lines · `File_3.csv` depots · `File_4.csv` trajectory 2026–2035 | `outputs/` |
| 3 | One self-contained HTML visualisation (4 views) + static captures | `outputs/` |
| 4 | Analytical report, 3–5 pages + annexes | outside this repo |
| 5 | 5-minute pitch | outside this repo |

The jury reads saved outputs only and never re-runs code. Every step must leave a visible table, chart or `CHECK … PASS` line.

## Repository layout

```
notebooks/
  01_Madrid_Electrification_Main.ipynb   # writes File_1-4, the HTML and all checks
  02_Benchmark_GTFS.ipynb                # benchmark GTFS metrics: >= 3 of London, Paris, Berlin, Brussels, Helsinki, Copenhagen
  03_Exploratory_Questions.ipynb         # whiteboard questions Q1-Q6, answered or dropped with pointers; writes no File_1-4
  04_Scenario_Lab.ipynb                  # supplementary: retrofit and transition scenarios; writes no File_1-4
data_raw/        # downloads (git-ignored; re-fetched by the notebooks, logged in the data register)
data_derived/    # intermediates, e.g. benchmark_gtfs_intermediate.csv (git-ignored)
outputs/         # File_1-4.csv, HTML, PNG captures (tracked)
requirements.txt # packages for running the notebooks locally
```

## Main notebook sections (dependency order)

| § | Section | Output | Status (23 Nov 2026) |
|---|---|---|---|
| 0 | Setup and fixed parameters | parameter table; CO₂ factors with evidence (grid factor labelled P) | Done |
| 1 | Data acquisition | data register | Done |
| 2 | Reference day | Tue 17 Nov 2026 (kept and documented, D7); supply day 9 Jun 2026 | Done |
| 3 | Fleet baseline 31 Dec 2025 | 2,210 (D1), S0 pace, age profile | Done |
| 4 | Line model | File 2 metrics, per-bus and university sensitivities | Done |
| 5 | Depot allocation | rule, alternatives, 2021 check, reserve reconciliation, deadheading | Done |
| 6 | Depot power and readiness | File 3; needed MW under low / base / high; hot-day and N-line sensitivities; interim La Elipa-closed network | Done |
| 7 | Prioritisation | completes File 2; cumulative bus cap per year (B5) | Done |
| 8 | Scenarios S0 / S1 | File 4 (D2–D5); earliest credible year (2030 / 2033 / 2037–2040); gas and carbon exposure | Done |
| 9 | Benchmark | File 1 (Helsinki, Paris, London); grid-factor basis table | Done |
| 10 | Visualisation | HTML + static PNGs of views (i)–(iv) in `outputs/` | Done |
| 11 | Decision log and assumptions register | every row Done or Dropped; D1–D7 | Done |
| 12 | Final compliance cell | read-back of all four CSVs + cross-file checks | 46 PASS / 0 FAIL |

All four notebooks are executed with saved outputs. Notebook 04 reads notebook 01's exports and File 4 parameters (`data_derived/nb01_params.json`), so both run on the same inputs.

## Rules we work by

- **One parameter cell.** All fixed values from the brief (§4.5) live in `P`. No other cell hard-codes a number, so sensitivities only change inputs.
- **Label every value** with `assume(variable, value, label, evidence)`: **V** verified · **D** derived · **P** proxy · **A** assumption. It feeds the assumptions register.
- **Log every source** with `fetch(url, filename, note)`; files obtained by registration go in `data_raw/` and are logged with `manual=True`. No API keys or passwords in notebooks.
- **Visible checks.** Use `check(name, condition)` after each step.
- **Alternate code and text cells** (brief §5.1, scored under T5). Every code cell is preceded by a short markdown cell saying what it does and why; never put two code cells in a row.
- **Supplementary analyses** (alternative allocations, day mixes, sensitivities) are printed in the notebook, never written into `File_1-4.csv`.
- **Zero-emission = battery-electric + hydrogen fuel-cell only.** CNG and biomethane never count.

## Workflow

1. Open a notebook in Colab: **File → Open notebook → GitHub**, authorise private repos, pick this repo. To run locally instead, see [Run the notebooks locally](CONTRIBUTING.md#run-the-notebooks-locally).
2. Work on your section in a branch (`section-4-line-model`, …) or a scratch copy; keep cells short and call helpers.
3. Save back with **File → Save a copy in GitHub**, commit message `§4: peak_buses from supply data`, open a pull request.
4. Before submission: merge everything into `main`, **Runtime → Restart and run all** in a clean runtime, confirm the final compliance cell shows 0 FAIL, then **File → Download → .ipynb** and commit `outputs/`.

## Open items

Closed:
- [x] Reference day: Tue 17 Nov 2026 (GTFS), kept despite the A-5 / M-30 works (D7); `peak_buses` from Tue 9 Jun 2026 (16 Jun as a sensitivity) — §2
- [x] La Elipa: closed since 2022; works awarded (EUR 112.1M, up to 32 months), modelled from 2030 with alternative C as the interim network — §5–§7
- [x] Bus type per line: evidence first (line 34) + proxy, with a low / high bracket — §4
- [x] Depot connection MW: Sanchinarro and La Elipa evidenced (planned), the other three estimated, with low / high hypotheses — §6
- [x] Benchmark fleet, targets, charging models and grid factors for Helsinki, Paris and London — §9 (Berlin and Brussels not covered)
- [x] Spain's 2025 grid factor: 108.4 g/kWh verified against Red Eléctrica's REData (national 2025, 0.1084 t/MWh) — §0
- [x] Notebook 04 research questions (checked 23 Nov 2026): no CNG-to-battery kit exists for EMT's city buses; grid sensitivity 37.1 g/kWh by 2035 (PNIEC 2030, national basis); no EMT tender after 2027 yet; conversions charge at most 150 kW by plug; storage EUR 300/kWh installed, 85 % round trip; reserve buses 130 km/yr (proxy); lease term 12 years (EMT's own tenders)

Still open (stated in the report, not blocking):
- [ ] Lessor rate for leases: none published, so notebook 04 sets it above Spain's 10-year yield (3.802 %) and sweeps 4–6 %
- [ ] Denmark's grid CO₂ factor: Copenhagen stays out of File 1 until one is sourced
- [ ] No sourced price for grid reinforcement at Critical depots: listed as a capex exclusion in §8 (terminus chargers are now priced in notebook 04 §9.2: 18 points, about EUR 9.5 M, outside File 4)
