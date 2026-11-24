# §9 Helsinki benchmark: decisions, assumptions and sources

Branch `section-9-helsinki-file1` · 20 Nov 2026, updated 23 Nov 2026 (peer reference day moved to Tue 24 Nov 2026) · builds on PR #9 (merged 18 Nov 2026).
Every value below is also logged with `assume()` in the notebooks, so it appears in the §11 assumptions register.

## The Helsinki row of File 1

| Field | Value | Label | Where it comes from |
|---|---|---|---|
| city | Helsinki | | |
| operator | HSL (Helsinki Regional Transport Authority) | V | HSL is the authority for the whole area |
| reference_date | 2026-11-24 | A | Common peer day: the rolling feeds downloaded on 23 Nov 2026 no longer all cover Madrid's 17 Nov, so every GTFS peer uses the first regular Tuesday inside every feed (brief 4.4 allows a local day); inside the HSL feed's validity (10 Nov 2026 – 8 Jan 2027) |
| n_bus_lines | 390 | D | HSL GTFS, every bus route active on the reference day |
| daily_bus_km | 289,802.2 | D | HSL GTFS, `shape_dist_traveled` per trip (km) |
| fleet_total | 1,154 | D | 600 ÷ 0.52. HSL publishes no total |
| ze_fleet | 600 | V | HSL "Electric buses" page, table for 2025 |
| ze_share_pct | 52.0 | D | Computed in File 1: 600 ÷ 1,154 |
| fleet_data_year | 2025 | | |
| ze_target_year | 2035 | V | HSL: public transport in the region emission-free by 2035 |
| charging_model | Mixed | V | HSL: depots at night and in daytime breaks, quick charging at some terminals |
| energy_full_bev_mwh_day | 376.7 | D | Computed in File 1: 289,802.2 × 1.30 ÷ 1000 (brief factor) |
| grid_co2_g_kwh | 26 | V | Fingrid, 2025 average for electricity consumed in Finland |

## Decisions taken with the team (20 Nov 2026)

1. **Perimeter = whole HSL area.** The brief (§4.4) defines Helsinki as "HSL (whole HSL area)". PR #9 had used Helsinki city only, copying the Paris method. That figure is now a printed sensitivity, never written to File 1.
   - Whole HSL area: 390 lines, 289,802 km/day, 19,286 trips (Tue 24 Nov 2026).
   - Helsinki city only: 183 lines, 131,418 km/day (45 % of the area).
   - HSL's fleet figures cover the whole area, so the row is now consistent.
2. **Zero-emission fleet = 600 and total = 1,154.** HSL's page disagrees with itself: the table says 600 electric buses (52 %), the text says "approximately 650", "around half". We use the table.
3. **Grid factor = Fingrid 2025, 26 g/kWh.** It is the latest year and the same year as Madrid's.
4. **Charging model = "Mixed"** (depot plus opportunity charging, from HSL's own description; File 1 allows Depot, Opportunity or Mixed).

## Assumptions and how much they matter

| Assumption | Label | Alternative (sensitivity) | Effect |
|---|---|---|---|
| Reference day 24 Nov 2026 (common peer day) | A | Madrid's 17 Nov (no longer in every peer feed) | Re-run if the peer feeds are re-downloaded |
| Bus = route types 700–799 (HSL uses 701, 702, 704) | V | `route_type` 3 finds nothing | Without it the row is empty |
| ZE fleet 600 | V | 650 (page text) | Share unchanged at about 52 % |
| Fleet total 1,154 = 600 ÷ 0.52 | D | About 1,250 (650, "around half") | fleet_total +8 %; share unchanged |
| Grid 26 g/kWh, consumption-based (includes imports) | V | Statistics Finland production-based, latest 2024 (2022 was 67.5 g/kWh) | Madrid's 108.4 is generation-based, so the methods differ; say so in the report |
| Target 2035 covers all public transport | V | HSL's own operations: 2030 | |
| Peak buses on the road = trips running at the same minute | D | Vehicle blocks (not available: `block_id` empty for buses) | Lower bound: leaves out terminal layovers and spares |

## Cross-check of the fleet

- HSL publishes no bus total, and older sources give about 1,300–1,400 buses (ZeEUS report, Yle; late 2010s).
- The timetable gives a floor: **934 bus trips on the road at once at 08:08** on 24 Nov 2026 (notebook 02).
- 934 is 81 % of 1,154. The remaining 19 % covers buses waiting at terminals plus spares, which is plausible.
- For comparison, Madrid's working-day peak in service is 1,692 against a fleet of 2,210 (77 %).

## Data cleaning (same steps as Madrid, notebook 03)

- Every table is read as text, padded text is stripped and exact duplicate rows are dropped.
  - No duplicates were found.
  - 16,307 padded cells were found, all in station rows that buses don't use.
- The feed has no `frequencies.txt`: every trip is a real run, so nothing is expanded.
- High-km lines are flagged with the 1.5 × IQR rule and kept (30 lines on the whole area, all trunk and cross-town routes).
- Trip km from `stop_times` matches the shape length for every trip (median ratio 1.0000).

## Checks (all PASS on a local run, 23 Nov 2026)

Notebook 02:
- reference day inside the feed validity
- no exact duplicate trips
- every bus trip has a shape and stop times
- no `frequencies.txt`
- trip km positive and matches shape length
- city km never exceed the trip km
- result follows the `city_metrics()` contract
- File 1 row uses the whole HSL area
- peak trips on the road below the derived fleet

Notebook 01 §9:
- zero-emission fleet does not exceed the fleet
- derived share matches HSL's 52 %

## Sources

- HSL, Electric buses (600 / 52 %, ~650 in text, charging, 2035 target): https://www.hsl.fi/en/hsl/electric-buses
- HSL, Carbon-neutral public transport (2035; own operations 2030): https://hsl.fi/en/hsl/responsibility/carbon-neutral-public-transport
- Fingrid, climate impact (26 gCO₂/kWh in 2025): https://www.fingrid.fi/en/grid/land-use-and-environment/environmental-impacts-of-transmission-lines/climate-impact/
- HSL GTFS snapshot `hsl_gtfs.zip`, valid 2026-11-10 to 2027-01-08, sha256 `54e907e2e93f…` (data register): https://infopalvelut.storage.hsldev.com/gtfs/hsl.zip
- Statistics Finland emission coefficients, table 14qt (alternative factor): https://pxdata.stat.fi/PXWeb/pxweb/en/StatFin/StatFin__ehk/14qt.px

## Status (24 Nov 2026)

- File 1 is assembled in the main notebook §9: the GTFS benchmark merged with the cited figures, with `ze_share_pct` and `energy_full_bev_mwh_day` computed.
- Paris perimeter: File 1 uses every km of the lines serving the City of Paris (Paris and inner ring, as the brief says); km inside Paris only is printed as a sensitivity in notebook 02.
- Run end to end locally; the final Colab "Restart and run all" pass is the last step before submission (README workflow).
