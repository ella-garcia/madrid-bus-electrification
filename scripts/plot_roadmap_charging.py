"""Plot EMT Madrid e-bus roadmap: charging capacity by depot vs e-buses in fleet.

Usage (from the repo root):
    python scripts/plot_roadmap_charging.py
    python scripts/plot_roadmap_charging.py --csv data/financial_model/roadmap_charging_by_depot.csv \
        --out figures/roadmap_charging_by_depot.png

Data comes from the financial model (target year 2033). See docs/financial_model.md.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DEPOTS = [
    ("existing_chargers", "Existing chargers (456)", "#888780"),
    ("carabanchel_27", "Carabanchel +27 (2026)", "#eb6834"),
    ("sanchinarro_114", "Sanchinarro +114 (2027)", "#2a78d6"),
    ("entrevias_465", "Entrevías +465 (2028)", "#1baf7a"),
    ("la_elipa_318", "La Elipa +318 (2029)", "#eda100"),
    ("carab_sanch_rest_199", "Carabanchel + Sanchinarro rest +199 (2030)", "#6250d6"),
    ("las_tablas_650", "Las Tablas +650 (2031)", "#e87ba4"),
]
PHASES = [  # (label, first year, last year, buses bought)
    ("Phase 1\ncommitted", 2026, 2027),
    ("Phase 2\nscale-up", 2028, 2030),
    ("Phase 3\nclose-out", 2031, 2033),
    ("Phase 4\nrenewals", 2034, 2035),
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=root / "data/financial_model/roadmap_charging_by_depot.csv")
    parser.add_argument("--out", default=root / "figures/roadmap_charging_by_depot.png")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    years = df["year"]

    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=150)
    bottom = pd.Series(0.0, index=df.index)
    for col, label, color in DEPOTS:
        ax.bar(years, df[col], bottom=bottom, width=0.6, color=color, label=label,
               edgecolor="white", linewidth=1)
        bottom += df[col]

    ax.plot(years, df["ebuses_in_fleet"], color="#0b0b0b", linewidth=2, linestyle="--",
            marker="o", markersize=5, label="E-buses in fleet (plan)", zorder=5)

    for _, row in df.iterrows():
        if row["spare_capacity"] < 0:
            ax.annotate(f"{int(-row['spare_capacity'])} short", (row["year"], row["ebuses_in_fleet"]),
                        xytext=(0, 10), textcoords="offset points", ha="center", fontsize=8,
                        color="#a32d2d")

    for i, (label, start, end) in enumerate(PHASES):
        bought = df.loc[df["year"].between(start, end), "ebuses_purchased"].sum()
        if i % 2 == 0:
            ax.axvspan(start - 0.5, end + 0.5, color="#f1efe8", zorder=0)
        ax.text((start + end) / 2, 2330, f"{label}\n{bought:,.0f} buses bought",
                ha="center", va="bottom", fontsize=8.5, color="#444441")

    ax.set_xticks(years)
    ax.set_ylim(0, 2750)
    ax.set_ylabel("Buses")
    ax.set_title("EMT Madrid zero-emission roadmap (target 2033): charging capacity by depot vs e-buses",
                 fontsize=11, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.08), ncol=3, fontsize=8, frameon=False)
    fig.text(0.01, 0.005,
             "Depot split beyond La Elipa (contracted) and Las Tablas (City plan) is the team's proposal; "
             "EMT does not publish buses per depot.",
             fontsize=7.5, color="#5f5e5a")
    fig.tight_layout(rect=(0, 0.02, 1, 1))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
