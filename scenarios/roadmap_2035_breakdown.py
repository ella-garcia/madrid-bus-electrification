"""Depot-by-depot cost breakdown of the 2035 roadmap (the tables in the roadmap document).

Reads the outputs of roadmap_2035.py and prints, for each depot in conversion order and each year:
e-buses (new and renewed), bus cost, chargers, charger equipment and installation, grid equipment
and works, building and civil works, an estimate of labour, and totals. Also prints the totals by
depot, by type of spending and by year, and writes them to results/roadmap_2035/breakdown.md.

Labour = 50 % of every works line (N10, our estimate, approved 26 Nov 2026).
Run:  python scenarios/roadmap_2035.py   then   python scenarios/roadmap_2035_breakdown.py
"""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parent / "results" / "roadmap_2035"
ORDER = ["Carabanchel", "Sanchinarro", "La Elipa", "Entrevias", "Fuencarral"]
LABOUR_IN_WORKS = 0.50  # N10


def column(item):
    if item == "e-buses replacing gas": return "bus_new"
    if item == "e-buses renewing e-buses": return "bus_renew"
    if item == "charger equipment": return "chg_eq"
    if item == "charger installation works": return "chg_works"
    if "building" in item: return "building"
    if "equipment" in item: return "grid_eq"
    return "grid_works"


def breakdown():
    K = pd.read_csv(OUT / "costs_by_depot.csv")
    K["c"] = K.item.map(column)
    K["labour"] = K.eur.where(K.item.str.contains("works|engineering"), 0) * LABOUR_IN_WORKS
    P = K.pivot_table(index=["depot", "year"], columns="c", values="eur", aggfunc="sum", fill_value=0) / 1e6
    U = K[K.c.isin(["bus_new", "bus_renew", "chg_eq"])].pivot_table(index=["depot", "year"], columns="c",
                                                                      values="units", aggfunc="sum", fill_value=0)
    P = P.join(U.add_prefix("n_"), how="left").fillna(0).join(K.groupby(["depot", "year"]).labour.sum() / 1e6)
    for c in ["bus_new", "bus_renew", "chg_eq", "chg_works", "grid_eq", "grid_works", "building",
              "n_bus_new", "n_bus_renew", "n_chg_eq"]:
        if c not in P: P[c] = 0.0
    P["buses"] = P.bus_new + P.bus_renew
    P["depot_total"] = P[["chg_eq", "chg_works", "grid_eq", "grid_works", "building"]].sum(axis=1)
    P["total"] = P.buses + P.depot_total
    return K, P


def to_markdown(K, P):
    lines = []
    head = ("| Year | E-buses new (renewed) | Buses €M | Chargers | Charger equipment €M | Charger installation €M "
            "| Grid equipment €M | Grid works €M | Building €M | Labour (est.) €M | Total €M |")
    for d in ORDER:
        x = P.loc[d]
        lines += [f"\n### {d}\n", head, "|" + "---|" * 11]
        for y, r in x.iterrows():
            if r.total < 0.05:
                continue
            lines.append(f"| {y} | {int(r.n_bus_new)} ({int(r.n_bus_renew)}) | {r.buses:.1f} | {int(r.n_chg_eq)} | {r.chg_eq:.1f} "
                         f"| {r.chg_works:.1f} | {r.grid_eq:.1f} | {r.grid_works:.1f} | {r.building:.1f} | {r.labour:.1f} | {r.total:.1f} |")
        s = x.sum()
        lines.append(f"| **Total** | **{int(s.n_bus_new)} ({int(s.n_bus_renew)})** | **{s.buses:.1f}** | **{int(s.n_chg_eq)}** "
                     f"| {s.chg_eq:.1f} | {s.chg_works:.1f} | {s.grid_eq:.1f} | {s.grid_works:.1f} | {s.building:.1f} "
                     f"| {s.labour:.1f} | **{s.total:.1f}** |")
    T = P.groupby("depot")[["n_bus_new", "n_bus_renew", "buses", "n_chg_eq", "depot_total", "labour", "total"]].sum().loc[ORDER]
    lines += ["\n### By depot\n", T.round(1).to_markdown(), "\n", T.sum().round(1).to_frame("total").T.to_markdown()]
    item = K.assign(k=K.item.where(~K.item.str.contains("grid|substation"), "grid upgrades and new substations")) \
            .groupby("k").eur.sum().div(1e6).sort_values(ascending=False)
    lines += ["\n### By type of spending (€M)\n", item.round(1).to_frame("€M").assign(
        share=(100 * item / item.sum()).round(0)).to_markdown()]
    yr = P.groupby("year")[["buses", "depot_total", "total"]].sum()
    lines += ["\n### By year (€M)\n", yr.round(1).to_markdown()]
    return "\n".join(lines)


if __name__ == "__main__":
    K, P = breakdown()
    md = to_markdown(K, P)
    (OUT / "breakdown.md").write_text(md, encoding="utf8")
    print(md)
    print(f"\nTotal €{K.eur.sum() / 1e6:,.1f}M  (written to {OUT / 'breakdown.md'})")
