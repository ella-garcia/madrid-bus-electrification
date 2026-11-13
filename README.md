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
  02_Benchmark_GTFS.ipynb                # Helsinki, Berlin, Paris, Brussels GTFS metrics
  03_Exploratory_Questions.ipynb         # whiteboard questions Q1-Q6; feeds the main notebook, writes no File_1-4
data_raw/        # downloads (git-ignored; re-fetched by the notebooks, logged in the data register)
data_derived/    # intermediates, e.g. benchmark_gtfs_intermediate.csv (git-ignored)
outputs/         # File_1-4.csv, HTML, PNG captures (tracked)
```

## Main notebook sections (dependency order)

| § | Section | Output | Owner |
|---|---|---|---|
| 0 | Setup and fixed parameters | parameter table | [owner] |
| 1 | Data acquisition | data register | [owner] |
| 2 | Reference day | chosen dates and gap workaround | [owner] |
| 3 | Fleet baseline 31 Dec 2025 | baseline, S0 pace, age profile | [owner] |
| 4 | Line model | File 2 metrics, per-bus sensitivity | [owner] |
| 5 | Depot allocation | rule, alternative, 2021 check, reserve reconciliation | [owner] |
| 6 | Depot power and readiness | File 3 | [owner] |
| 7 | Prioritisation | completes File 2 | [owner] |
| 8 | Scenarios S0 / S1 | File 4, earliest credible year, sensitivities | [owner] |
| 9 | Benchmark | File 1 | [owner] |
| 10 | Visualisation | HTML + static views | [owner] |
| 11 | Assumptions register | register | [owner] |
| 12 | Final compliance cell | read-back of all four CSVs + cross-file checks | already written |

Sections 0, 4 (formulas), 6 (`depot_table`) and 12 are already implemented from the brief's fixed formulas; the rest are `TODO(owner: …)` cells.

## Rules we work by

- **One parameter cell.** All fixed values from the brief (§4.5) live in `P`. No other cell hard-codes a number, so sensitivities only change inputs.
- **Label every value** with `assume(variable, value, label, evidence)`: **V** verified · **D** derived · **P** proxy · **A** assumption. It feeds the assumptions register.
- **Log every source** with `fetch(url, filename, note)`; files obtained by registration go in `data_raw/` and are logged with `manual=True`. No API keys or passwords in notebooks.
- **Visible checks.** Use `check(name, condition)` after each step.
- **Supplementary analyses** (alternative allocations, day mixes, sensitivities) are printed in the notebook, never written into `File_1-4.csv`.
- **Zero-emission = battery-electric + hydrogen fuel-cell only.** CNG and biomethane never count.

## Workflow

1. Open a notebook in Colab: **File → Open notebook → GitHub**, authorise private repos, pick this repo.
2. Work on your section in a branch (`section-4-line-model`, …) or a scratch copy; keep cells short and call helpers.
3. Save back with **File → Save a copy in GitHub**, commit message `§4: peak_buses from supply data`, open a pull request.
4. Before submission: merge everything into `main`, **Runtime → Restart and run all** in a clean runtime, confirm the final compliance cell shows 0 FAIL, then **File → Download → .ipynb** and commit `outputs/`.

## Open items (from the dataset tracker)

- [ ] Reference day: GTFS valid from 6 Nov 2026, supply data ends Sep 2026 — use the closest equivalent weekday for `peak_buses` and document it
- [ ] La Elipa depot status (closed Mar 2022 for rebuilding)
- [ ] Bus type per line (only line 34 known) — proxy needed
- [ ] Depot connection MW: Sanchinarro evidenced (8 MW + 5 MW backup); others by proxy
- [ ] Benchmark fleet, targets and charging models at 31 Dec 2025; grid CO₂ factors for Germany, Finland, Belgium
