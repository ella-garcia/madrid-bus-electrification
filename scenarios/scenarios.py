"""Scenario registry, in three groups. Each entry overrides BASE; `deliveries` is a schedule
function (year, state) -> buses wanted that year before the intake and budget caps."""
import math

S0_PACE = 77        # DATA: 2021-25 zero-emission buses added a year (notebook 01 §3: 77.2)
BUDGET_PACE = 65    # WEB: EMT budgets buy 70 e-buses in 2026 and 65 in 2027


def pace(n):
    return lambda y, s: s["due_ze"] + n


def target(year):
    def f(y, s):
        left = max(0, s["cng_left"] - s["pool"])
        return s["due_ze"] + math.ceil(left / max(1, year - y + 1))
    return f


def as_fast_as_possible(y, s):
    return s["due_ze"] + max(0, s["cng_left"] - s["pool"])


def at_end_of_life(y, s):
    return s["due_ze"] + max(0, s["due_cng"] - s["pool"])


def pace_then_target(n, until, year):
    t = target(year)
    return lambda y, s: (s["due_ze"] + n) if y <= until else t(y, s)


WHAT_IT_TAKES = dict(first_order_delivery=2027, max_intake=450)

SCENARIOS = [
    # ---- A. current pace
    dict(group="A. Current pace", name="A1 Historic pace (77/yr)", deliveries=pace(S0_PACE), power="grid",
         note="Brief S0: the 2021-25 pace of 77 zero-emission buses a year"),
    dict(group="A. Current pace", name="A2 Budgeted pace (65/yr)", deliveries=pace(BUDGET_PACE), power="grid",
         note="EMT's own 2026-27 budgets: 70 and 65 e-buses a year"),
    # ---- B. 2030 target
    dict(group="B. 2030 target", name="B1 2030, grid only", deliveries=target(2030), power="grid",
         note="Brief S1, depots wait for grid upgrades (ordered 2027, ready 2030)"),
    dict(group="B. 2030 target", name="B2 2030, batteries + grid", deliveries=target(2030), power="bess+grid",
         note="Batteries bridge from 2028 until the grid arrives"),
    dict(group="B. 2030 target", name="B3 2030, batteries take 2 years", deliveries=target(2030), power="bess+grid",
         bess_lead_years=2, note="As B2 with the web's 12-24 month battery lead time"),
    dict(group="B. 2030 target", name="B4 2030, what it would take", deliveries=target(2030), power="bess+grid",
         **WHAT_IT_TAKES, note="Orders delivered from 2027 and 450 buses a year (two suppliers in parallel)"),
    dict(group="B. 2030 target", name="B5 2030, what it takes + flexible grid", deliveries=target(2030), power="bess+grid",
         flexible_access=True, **WHAT_IT_TAKES, note="B4 with CNMC flexible access: connections in 2 years for EUR 2M"),
    dict(group="B. 2030 target", name="B6 2030, what it takes + hydrogen", deliveries=target(2030), power="bess+grid",
         over_range_tech="H2", **WHAT_IT_TAKES, note="B4 with hydrogen buses on the 6 over-range lines"),
    dict(group="B. 2030 target", name="B7 2030, gas take-or-pay 80 %", deliveries=target(2030), power="bess+grid",
         gas_take_or_pay=0.8, **WHAT_IT_TAKES, note="B4 if the biomethane contract makes EMT pay for 80 % of its volume"),
    # ---- C. other paths
    dict(group="C. Other paths", name="C1 Target 2032", deliveries=target(2032), power="bess+grid",
         note="Spread purchases to finish in 2032"),
    dict(group="C. Other paths", name="C2 Target 2033 (Madrid's goal)", deliveries=target(2033), power="bess+grid",
         note="The city's stated 2033 goal"),
    dict(group="C. Other paths", name="C3 Replace at 12 years", deliveries=at_end_of_life, power="grid",
         note="No early scrapping"),
    dict(group="C. Other paths", name="C4 Replace at 12 years, batteries only", deliveries=at_end_of_life, power="bess",
         note="No grid upgrades at all"),
    dict(group="C. Other paths", name="C5 Gas contract first, then sprint", deliveries=pace_then_target(BUDGET_PACE, 2029, 2033),
         power="bess+grid", note="Budgeted pace through the 2027-29 gas contract, then finish by 2033"),
    dict(group="C. Other paths", name="C6 Depot by depot", deliveries=target(2032), power="bess+grid", order="depot_sequence",
         depot_sequence=["Carabanchel", "Sanchinarro", "Fuencarral", "Entrevias", "La Elipa"],
         note="Finish one depot at a time (Carabanchel, Sanchinarro, Fuencarral, Entrevias, La Elipa)"),
    dict(group="C. Other paths", name="C7 Budget EUR 150M a year", deliveries=as_fast_as_possible, power="bess+grid",
         budget_cap_meur=150, note="As fast as a EUR 150M yearly cap on buses, chargers and power allows"),
    dict(group="C. Other paths", name="C8 Budget EUR 200M a year", deliveries=as_fast_as_possible, power="bess+grid",
         budget_cap_meur=200, note="Same with EUR 200M"),
    dict(group="C. Other paths", name="C9 La Elipa late (2032)", deliveries=target(2032), power="bess+grid",
         la_elipa_open=2032, note="C1 if La Elipa opens in 2032"),
    dict(group="C. Other paths", name="C10 Bus life 14 years", deliveries=at_end_of_life, power="grid",
         bus_life=14, note="C3 if buses last 14 years"),
    dict(group="C. Other paths", name="C11 Riders first", deliveries=target(2032), power="bess+grid", order="riders_desc",
         note="C1 converting the busiest lines first"),
]

# ---- D. optimised (best feasible plan per finish year from optimize.py, base supply assumptions)
DEPOT_SEQ = ["Carabanchel", "Sanchinarro", "Fuencarral", "Entrevias", "La Elipa"]
BEST = dict(power="bess+grid", flexible_access=True, over_range_tech="BEV", order="depot_sequence", depot_sequence=DEPOT_SEQ)
FLEX = dict(power="grid", flexible_access=True, over_range_tech="BEV", order="depot_sequence", depot_sequence=DEPOT_SEQ)
GRID = dict(power="grid", over_range_tech="BEV", order="depot_sequence", depot_sequence=DEPOT_SEQ)
SCENARIOS += [
    dict(group="D. Optimised", name="D1 Best 2032", deliveries=target(2032), **BEST,
         note="Fastest with today's limits: depot by depot, batteries + flexible grid (lowest NPV for 2032)"),
    dict(group="D. Optimised", name="D2 Best 2033 (recommended)", deliveries=target(2033), **BEST,
         note="Madrid's 2033 goal with the lowest peak yearly spend: batteries + flexible grid, depot by depot"),
    dict(group="D. Optimised", name="D2b 2033, no batteries (lowest NPV)", deliveries=target(2033), **FLEX,
         note="Madrid's 2033 goal at the lowest NPV: flexible grid only; buses wait for power, then a steeper ramp"),
    dict(group="D. Optimised", name="D3 Best 2034", deliveries=target(2034), **GRID,
         note="Lowest NPV for 2034: standard grid upgrades only, depot by depot"),
    dict(group="D. Optimised", name="D4 Best 2035", deliveries=target(2035), **GRID,
         note="Lowest NPV for 2035: standard grid upgrades only, almost no early scrapping"),
]

# ---- B8: best way to 2030 found by optimize.py (lowest NPV among the 2030 plans with the fewest idle buses)
SCENARIOS.insert(
    [i for i, s in enumerate(SCENARIOS) if s["name"].startswith("B7")][0] + 1,
    dict(group="B. 2030 target", name="B8 Best with tender only", deliveries=target(2030), power="bess+grid",
         flexible_access=True, over_range_tech="BEV", order="riders_desc", **WHAT_IT_TAKES,
         note="Tender now (2027, 450/yr), batteries + flexible grid, busiest lines first; power still ordered 2027"))

# ---- B9: all-in for 2030 = tender now + depot batteries and grid permits ordered now (Dec 2026)
ALL_IN = dict(first_order_delivery=2027, max_intake=450, decision_year=2026)
SCENARIOS.insert(
    [i for i, s in enumerate(SCENARIOS) if s["name"].startswith("B8")][0] + 1,
    dict(group="B. 2030 target", name="B9 Best 2030: all-in now", deliveries=target(2030), power="bess+grid",
         flexible_access=True, over_range_tech="BEV", order="depot_sequence", depot_sequence=DEPOT_SEQ, **ALL_IN,
         note="Best 2030 plan found: tender now, batteries + flexible grid ordered in Dec 2026, depot by depot"))
