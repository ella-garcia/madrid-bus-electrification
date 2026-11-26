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

| § | Section | Output | Status (24 Nov 2026) |
|---|---|---|---|
| 0 | Setup and fixed parameters | parameter table; CO₂ factors with evidence (grid factor V, Red Eléctrica REData) | Done |
| 1 | Data acquisition | data register | Done |
| 2 | Reference day | Tue 17 Nov 2026 (kept and documented, D7); supply day 9 Jun 2026 | Done |
| 3 | Fleet baseline 31 Dec 2025 | 2,210 (D1), S0 pace, age profile | Done |
| 4 | Line model | File 2 metrics, per-bus and university sensitivities | Done |
| 5 | Depot allocation | rule, alternatives, 2021 check, reserve reconciliation, deadheading | Done |
| 6 | Depot power and readiness | File 3; needed MW under low / base / high; hot-day and N-line sensitivities; interim La Elipa-closed network | Done |
| 7 | Prioritisation | completes File 2; cumulative bus cap per year, 2027–29 evened around the La Elipa and Fuencarral floors | Done |
| 8 | Scenarios S0 / S1 | File 4 (D2–D5, D8: no gas purchases); earliest credible year (2030 / 2033 / 2037–2040 at 165–200 buses a year; 2036 on 13-year renewals); gas and carbon exposure | Done |
| 9 | Benchmark | File 1 (Helsinki, Paris, London, Copenhagen, Berlin); grid-factor basis table | Done |
| 10 | Visualisation | HTML + static PNGs of views (i)–(iv) in `outputs/` | Done |
| 11 | Decision log and assumptions register | every row Done or Dropped; D1–D9 | Done |
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
4. Before submission: merge everything into `main`, run all four notebooks in one runtime as described in [Run all four notebooks](#run-all-four-notebooks), confirm each notebook's final check cell shows 0 FAIL, then download the four `.ipynb` files and commit them with `outputs/`.

## Run all four notebooks

**Order matters.** Each notebook reads files written by an earlier one:

| Order | Notebook | Reads | Writes |
|---|---|---|---|
| 1 | `02_Benchmark_GTFS` | peer-city GTFS feeds | `data_derived/benchmark_gtfs_intermediate.csv` |
| 2 | `01_Madrid_Electrification_Main` | EMT data, notebook 02's benchmark file | `outputs/File_1-4.csv`, views, `data_derived/` tables incl. `nb01_params.json` |
| 3 | `03_Exploratory_Questions` | EMT data, `outputs/File_1-4.csv` | printed answers; cleaned tables in `data_derived/` that no other notebook reads |
| 4 | `04_Scenario_Lab` | notebook 01's `data_derived/` tables, `outputs/File_1-4.csv`, `notes/` | printed scenarios only; writes no files |

Notebooks 02, 03 and 04 also read notebook 01's parameter cell straight from `notebooks/01_Madrid_Electrification_Main.ipynb`, so all four must run inside a full copy of the repo.

**Locally.** Do the one-time setup in [Run the notebooks locally](CONTRIBUTING.md#run-the-notebooks-locally) (`.venv`, `requirements.txt`, the team's GTFS snapshot at `data_raw/emt_gtfs.zip`). Then either open `jupyter lab notebooks/` and use **Run → Run All Cells** on each notebook in the order above, or run them all from the repo folder:

```bash
cd notebooks && for nb in 02_Benchmark_GTFS 01_Madrid_Electrification_Main 03_Exploratory_Questions 04_Scenario_Lab; do jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 "$nb.ipynb" || break; done
```

**In Colab.** Opening each notebook from GitHub and pressing *Run all* does not work: every Colab notebook runs on its own machine, so the files one notebook writes never reach the next. Run all four inside **one** runtime instead:

1. Open a new, blank Colab notebook.
2. Add a GitHub token as a Colab secret named `GH_TOKEN` (key icon in the left sidebar) and give the notebook access to it. The repo is private; the secret keeps the token out of the notebook. Never paste a token into a cell.
3. Clone the repo to the folder the notebooks expect, `/content/datathon`:

   ```python
   from google.colab import userdata
   import subprocess
   REPO = "github.com/ella-garcia/madrid-bus-electrification.git"
   subprocess.run(["git", "clone", f"https://{userdata.get('GH_TOKEN')}@{REPO}", "/content/datathon"], check=True)
   subprocess.run(["git", "-C", "/content/datathon", "remote", "set-url", "origin", f"https://{REPO}"], check=True)  # drop the token from .git/config
   ```

4. Upload **only** the team's GTFS snapshot, `emt_gtfs.zip` (about 21 MB, from the [shared Drive folder](https://drive.google.com/drive/folders/18E-C6Zx7Kij4J3WnIfDKsCHC2hTds4Rm); if Drive shows a virus-scan page, click *Download anyway*). Do not upload the notebooks: the clone already has them. The cell refuses any other file:

   ```python
   import hashlib, os
   from google.colab import files
   p = "/content/datathon/data_raw/emt_gtfs.zip"
   os.makedirs(os.path.dirname(p), exist_ok=True)
   up = files.upload()                  # pick emt_gtfs.zip only
   name, data = next(iter(up.items()))
   sha = hashlib.sha256(data).hexdigest()[:12]
   assert sha == "62453fb95492", f"{name}: {len(data):,} bytes, checksum {sha} - not the team GTFS snapshot"
   with open(p, "wb") as f:
       f.write(data)
   if os.path.exists(name):
       os.remove(name)
   print("OK:", len(data), "bytes, checksum", sha)
   ```

5. Run the four notebooks in order (this takes a while and stops at the first failure):

   ```python
   %cd /content/datathon/notebooks
   !for nb in 02_Benchmark_GTFS 01_Madrid_Electrification_Main 03_Exploratory_Questions 04_Scenario_Lab; do jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 $nb.ipynb || break; done
   ```

6. Check that notebook 01's data register shows checksum `62453fb95492` for `emt_gtfs.zip` and that notebooks 01 and 04 end with 0 FAIL (no saved output should contain `CHECK FAIL`). Expect File 1's Helsinki and Paris km to differ slightly from `main`: both feeds are republished daily and downloaded fresh in Colab.
7. Export read-only HTML copies (nothing is re-run) and download everything in one zip, then commit it from your machine:

   ```python
   %cd /content/datathon
   !rm -f /content/colab_run.zip && mkdir -p outputs/notebooks_html
   !jupyter nbconvert --to html --output-dir outputs/notebooks_html notebooks/0*.ipynb
   !zip -qr /content/colab_run.zip notebooks/*.ipynb outputs
   from google.colab import files
   files.download("/content/colab_run.zip")
   ```

   The HTML files in `outputs/notebooks_html/` open in any browser with every output visible, so a reader does not need to run anything.

## Open items

Closed:
- [x] Reference day: Tue 17 Nov 2026 (GTFS), kept despite the A-5 / M-30 works (D7); `peak_buses` from Tue 9 Jun 2026 (16 Jun as a sensitivity) — §2
- [x] La Elipa: closed since 2022; works awarded (EUR 112.1M, up to 32 months), modelled from 2030 with alternative C as the interim network — §5–§7
- [x] Bus type per line: evidence first (line 34) + proxy, with a low / high bracket — §4
- [x] Depot connection MW: Sanchinarro and La Elipa evidenced (planned), the other three estimated, with low / high hypotheses — §6
- [x] Benchmark fleet, targets, charging models and grid factors for Helsinki, Paris, London, Copenhagen and Berlin — §9 (Brussels not covered)
- [x] Denmark's 2025 grid factor: Energinet Miljødeklaration (125 % method), hourly Final values weighted by consumption (D); Copenhagen added to File 1 on 26 Nov 2026 — §9
- [x] Spain's 2025 grid factor: 108.4 g/kWh verified against Red Eléctrica's REData (national 2025, 0.1084 t/MWh) — §0
- [x] Notebook 04 research questions (checked 23 Nov 2026): no CNG-to-battery kit exists for EMT's city buses; grid sensitivity 37.1 g/kWh by 2035 (PNIEC 2030, national basis); no EMT tender after 2027 yet; conversions charge at most 150 kW by plug; storage EUR 300/kWh installed, 85 % round trip; reserve buses 130 km/yr (proxy); lease term 12 years (EMT's own tenders)

Still open (stated in the report, not blocking):
- [ ] Lessor rate for leases: none published, so notebook 04 sets it above Spain's 10-year yield (3.802 %) and sweeps 4–6 %
- [ ] No sourced price for grid reinforcement at Critical depots: listed as a capex exclusion in §8 (terminus chargers are now priced in notebook 04 §9.2: 18 points, about EUR 9.5 M, outside File 4)
