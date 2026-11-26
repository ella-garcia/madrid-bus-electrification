# Depot-by-depot roadmap to 100 % by 2035 (26 Nov 2026)

Local note, branch `research-scenario-inputs`.
- **Model:** `scenarios/roadmap_2035.py`
- **Results:** `scenarios/results/roadmap_2035/` (depots_by_year, years, moves, retirements, infrastructure, checks). All 8 checks PASS.

## Rules
1. **Retire oldest first.** Each retired gas bus is replaced by a new e-bus. 2026–27 follow the 120 awarded e-buses (70 + 50). From 2028, orders are spread evenly to 2035, but no gas bus is retired before it is 12.
2. **Renew e-buses at 12,** like for like, at their own depot (264 renewals in 2030–35).
3. **New e-buses go to one depot at a time.** Order: Carabanchel → Sanchinarro → La Elipa → Entrevías → Fuencarral / Las Tablas. A depot takes an e-bus only if it has a charging position (up to 120 new a year) and grid power for it.
4. **Gas buses move out** of the depot being electrified, into places freed by scrapping at the other depots. Scrapping prefers the depot being electrified, so fewer buses move.
5. **La Elipa reopens all-electric in 2030.** Until it is full, its lines stay at the other four depots.
6. **Las Tablas (650 places, all-electric) replaces Fuencarral from 2032.**

## Results (constant 2025 €, excluding VAT)

| | Value |
|---|---|
| 100 % zero-emission | 2035 (49 % in 2030, 80 % in 2033) |
| Gas buses scrapped under 12 | 0. All retire at 12–13, except the 2010 group, retired at 16 in 2026 |
| E-buses bought | 2,012: 1,748 replace gas, 264 renew e-buses |
| Buses a year | 48 (2028), then 243–315 (2030–35); EMT's record is 382 |
| Investment 2026–35 | €1,726M: e-buses €1,252M, Las Tablas €230M, La Elipa €134M, chargers €100M, grid upgrades €10M |
| Peak year | €272M (2029: La Elipa and Las Tablas works overlap) |
| Gas buses moved between depots | 409 over 2026–33 |

**Each depot fully electric by:**
- Carabanchel: 2031 (its own lines in 2027; until 2031 it also runs La Elipa lines with gas)
- Sanchinarro: 2031
- La Elipa: 2031 (opens 2030)
- Entrevías: 2035
- Fuencarral / Las Tablas: 2035

**Slack:** Las Tablas could open as late as 2033 without moving the date.

## New assumptions (approved by the user, 26 Nov 2026)
- **N1:** today's 452 e-buses by depot: Carabanchel 375, Fuencarral 44, Sanchinarro 22, Entrevías 11. EMT does not publish the split, so it is set from the charging points.
- **N2:** grid requests for Sanchinarro (+5.5 MW) and Entrevías (to 14 MW) are filed in 2026 and in service in 2029 (A6: 3 years), at €5M each (A7). The team keeps a €61.75M contingency for upstream grid works.
- **N3:** Las Tablas opens in 2032 with 650 places and 25 MW, at €229.45M (the team's model), spread over 2028–31.
- **N4:** buses per depot = File 3 active buses scaled to 2,210 (reserve spread pro rata). La Elipa's lines stay at the other four depots, pro rata, until it is full.
- **N5:** Sanchinarro keeps adding positions from 2028. 8 MW powers about 236 e-buses before the upgrade.
- **N6:** up to 120 new charging positions per depot a year (EMT's best pace, depot-chargers note C1).
- **N7:** no battery at any depot. Sanchinarro's 13.0 MW need is met by the grid upgrade.

## Extra (not in the model): blackout backup
- Battery energy per bus-day: 205 kWh (File 3: 451 MWh a day for the whole fleet).
- Battery: €250/kWh (A8), 90 % usable, 88 % round trip (A9).
- Islanding equipment: +12 % (estimate).

| Emergency service | Buses | Battery | Cost |
|---|---|---|---|
| 10 % | 220 | 63 MWh | €18M |
| 25 % | 550 | 158 MWh | €44M |
| 50 % | 1,100 | 316 MWh | €89M |

**Solar (estimate):**
- 5 MWp (about 1 MWp per depot), €4.5–6.5M.
- About 8,250 MWh a year, enough to recharge about 100 buses a day on average (about 57 in winter).
- Saves about €0.7M a year, so it pays back in 6–9 years.
- PV prices and yields are estimates to verify.

## Cost by depot (added 26 Nov 2026; `results/roadmap_2035/costs_by_depot.csv`)

| Order | Depot | Works | E-buses (new + renewed) | Buses €M | Depot €M | of which labour (est.) €M | Total €M |
|---|---|---|---|---|---|---|---|
| 1 | Carabanchel | 2026–27 | 110 + 220 | 207.7 | 11.4 | 2.3 | 219.1 |
| 2 | Sanchinarro | 2027–31 | 362 + 13 | 230.6 | 44.9 | 9.1 | 275.5 |
| 3 | La Elipa | 2027–29 (opens 2030) | 315 + 0 | 193.9 | 134.3 | 55.3 | 328.2 |
| 4 | Entrevías | 2027–35 | 442 + 5 | 278.2 | 53.6 | 10.8 | 331.8 |
| 5 | Fuencarral / Las Tablas | 2028–35 | 519 + 26 | 340.0 | 229.4 | 91.9 | 569.5 |
| | **Total** | | **1,748 + 264** | **1,250.5** | **473.6** | **169.4** | **1,724.1** |

**Bus price by depot:** the brief's €615k (12 m) and €800k (18 m), weighted by each depot's articulated share in File 2:
- Carabanchel: €629k (7.8 % articulated)
- Fuencarral: €624k (4.8 %)
- Entrevías: €622k (4.0 %)
- La Elipa: €616k (0.3 %)
- Sanchinarro: €615k (0 %)

**New split assumptions (approved by the user, 26 Nov 2026):**
- **N8:** a charging position at €110k all-in (A10) = 60 % equipment + 40 % installation works.
- **N9:** a grid upgrade at €5M (A7) = 55 % equipment + 45 % civil works and engineering. The same €5M is used for the new substations at La Elipa and Las Tablas, which is probably low.
- **N10:** labour is 50 % of every works line (charger installation, grid works, building and civil works).
- New depots: building and civil works = contract total − chargers − substation (La Elipa €94.3M, Las Tablas €152.9M).
