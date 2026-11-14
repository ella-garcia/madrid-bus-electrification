# Contributing

How to join the repo, work on your section and open a pull request. The rules for the notebooks themselves (parameters, `assume()`, `fetch()`, `check()`) are in [README.md](README.md#rules-we-work-by).

## Before you start

- **Access.** Ask Ella for a collaborator invite (repo Settings → Collaborators) and accept it. Without it you can't push branches.
- **Colab users.** Saving from Colab (File → Save a copy in GitHub) can't create a branch or check for conflicts the same way. Still run steps 6–7 below locally before you ask for a review.

## Conventions at a glance

| What | Convention | Example |
|---|---|---|
| Branch | `section-<N>-<short-kebab-description>`, from the latest `main` | `section-4-line-model` |
| Commit message | `§<N>: <what changed, imperative>`, with a bullet body when not obvious | `§4: peak_buses from supply data` |
| PR title | same as the commit format | `§4: peak_buses from supply data` |
| PR body | **What** · **Checks** · **Heads-up for other sections** · **Not done** | see [PR #1](https://github.com/ella-garcia/madrid-bus-electrification/pull/1) |
| Review | at least one teammate; never merge your own PR, no auto-merge | |

## Run the notebooks locally

Colab needs no setup. To run on your own machine you need **Python 3.10+** and an internet connection for the first run.

**1. Create an environment and install the packages** (once, from the repo folder):

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Get the shared GTFS snapshot.** EMT's GTFS link serves a new file every day, so each person downloading it gets different line km. Download the team's copy from the [shared Drive folder](https://drive.google.com/drive/folders/18E-C6Zx7Kij4J3WnIfDKsCHC2hTds4Rm) and save it as `data_raw/emt_gtfs.zip` **before** the first run (create `data_raw/` if it doesn't exist); `fetch()` never overwrites a file that is already there. After a run, the data register must show checksum `62453fb95492` for `emt_gtfs.zip`; if it doesn't, you have a different file. Colab users: upload the same file to `/content/datathon/data_raw/` before running. The other sources download automatically.

**3. Open the notebooks** with the environment active:

```bash
jupyter lab notebooks/
```

In VS Code, open a notebook and pick the `.venv` interpreter as the kernel. Either way the notebook must run from the `notebooks/` folder (the default), because it finds `data_raw/`, `data_derived/` and `outputs/` one level up.

**4. Run all cells** (Run → Run All Cells). Every `CHECK` line should say `PASS`. Downloads go to `data_raw/` and cleaned tables to `data_derived/`; both are git-ignored. The first run of notebook 03 takes under a minute.

Before committing, re-run the notebook top to bottom so the saved outputs match the code. The final submission run is still done in Colab (see the README workflow).

## Setup prompt for Claude Code

Fill in the two placeholders at the top, then paste the whole block into Claude Code in an empty folder.

````text
I'm joining my team's datathon repo: https://github.com/ella-garcia/madrid-bus-electrification
My section: §<N> <section name>   (e.g. §4 Line model — see the table in README.md)
My task: <one line, e.g. "compute peak_buses from the supply data">

Please set me up and help me contribute while following the team's conventions. Steps:

1. GitHub access
   - Check `gh auth status`. If I'm not logged in, run `gh auth login` (GitHub.com, HTTPS, browser) and let me do the browser step myself.
   - Check whether I can push to the repo: `gh repo view ella-garcia/madrid-bus-electrification --json viewerPermission`.
     If it's WRITE or higher, clone the repo directly. If not, stop and tell me to ask Ella for a collaborator invite. Only fork if I say so; in that case add the original repo as `upstream`.

2. Clone and look around
   - Clone the repo here, then read README.md and CONTRIBUTING.md fully. README has the rules: one parameter cell `P`, `assume()` labels, `fetch()` for sources, `check()` after every step, and zero-emission means only battery-electric and hydrogen buses.
   - Check that `.gitignore` excludes `data_raw/`, `data_derived/` and `.venv/`. Never commit downloaded data.
   - If I want to run the notebooks on my machine, follow "Run the notebooks locally" in CONTRIBUTING.md: create `.venv`, install `requirements.txt`, and before the first run tell me to download the team's GTFS snapshot from https://drive.google.com/drive/folders/18E-C6Zx7Kij4J3WnIfDKsCHC2hTds4Rm and save it as `data_raw/emt_gtfs.zip` (don't download the GTFS from EMT).

3. Branch
   - Run `git fetch origin && git switch main && git pull`, then create a branch from the latest main.
   - Name it `section-<N>-<short-kebab-description>`, e.g. `section-4-line-model`. One branch per section or task, and never commit to main directly.

4. Work
   - Only edit the cells of my section in `notebooks/` (they're marked `TODO(owner: …)`), plus the README checklist line if I close an open item. Don't reformat or re-run other people's sections. Changes to shared helpers (§0) need a note in the PR.
   - Keep cells short, never hard-code a number outside `P`, and label every value with `assume(...)`. End each step with a visible `check(...)`.
   - No API keys, tokens or passwords in notebooks or commits.

5. Commit
   - Commit message format: `§<N>: <what changed, imperative>`, e.g. `§4: peak_buses from supply data`.
   - Add a short body with bullet points when the change isn't obvious. Several small commits are better than one big one.

6. Merge-conflict check before opening the PR
   - Run `git fetch origin`, then `git merge origin/main` into my branch (don't rebase a branch that's already pushed).
   - If there are conflicts, show me each conflicting file and hunk and explain what each side changed. Notebooks (.ipynb) are JSON, so resolve them cell by cell and keep both teammates' cells. Ask me before discarding anything that isn't mine.
   - After resolving, check the notebook is still valid JSON:
     `python -c "import json,sys;json.load(open(sys.argv[1]))" notebooks/<file>.ipynb`
   - Then confirm `git diff origin/main --stat` only touches files I meant to change.

7. Pull request
   - Push with `git push -u origin <branch>` and open a PR into `main` with `gh pr create`:
     - Title: same format as the commit, `§<N>: <summary>`
     - Body sections: **What** (bullets), **Checks** (the CHECK lines my cells print, and whether they pass), **Heads-up for other sections** (anything that affects someone else's section), **Not done** (what's left, and whether it has been run in Colab)
   - Request a review from at least one teammate. Don't merge my own PR, and don't enable auto-merge.
   - Show me the PR link and run `gh pr view --json mergeable,mergeStateStatus`. If it isn't MERGEABLE/CLEAN, go back to step 6.

Ask me before any force-push, branch deletion, or change to someone else's section.
````
