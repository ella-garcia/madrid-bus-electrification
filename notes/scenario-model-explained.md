# Scenario lab: what every column means and where every number comes from

Local branch `research-scenario-inputs` · 20–21 Nov 2026 · all assumptions A1–A30 approved (A1–A13 on 20 Nov, A14–A30 on 21 Nov) · explains `scenarios/` (model.py, assumptions.py, scenarios.py).

**Where each input comes from:**
- **DATA**: our own datasets (EMT open data, GTFS, the planning conversation's processed tables).
- **WEB**: found on the internet, with the link.
- **BRIEF**: fixed by the datathon brief.
- **CALC**: calculated by the model from the other inputs.
- **ASSUMPTION**: my choice, not sourced.

## 1. The inputs the model starts from

| Input | Value | Type | Where it comes from |
|---|---|---|---|
| Fleet at 31 Dec 2025, by fuel, size and year bought | 2,210 = 452 BEV + 10 H₂ + 1,748 CNG | DATA | EMT fleet register `vehicles.csv` ([datos.madrid.es 300241](https://datos.madrid.es/dataset/300241-0-emt-flota-autobuses)), one record per vehicle |
| Lines: daily km, peak buses, bus type, technology | 234 lines, 339,220 km/day, 2,005 peak buses | DATA | Planning conversation's `line_table.csv`: GTFS 17 Nov 2026 + EMT bus-supply data (22 Sep 2026) + list of 45 electric lines |
| Depot of each line | Fuencarral 44, Carabanchel 55, Sanchinarro 57, Entrevías 49, La Elipa 29 lines | DATA, but old (P) | EMT `linesemt.csv`, mostly 2019–2024 records; depot codes inferred |
| Night energy per line | km/day × kWh/km (1.30 / 1.85) | CALC from DATA + BRIEF | `line_energy_kwh_day` |
| Lines above battery range | 6 lines (88, 164, 179, 200, 203, SE709) | CALC | km per bus-day > 300 km (standard) |

## 2. Assumptions behind the calculations

| # | Assumption | Value used | Type | Source / reasoning |
|---|---|---|---|---|
| — | kWh/km, range, CNG kg/km, 90 % charging efficiency, 7 h window | brief values | BRIEF | Brief §4.5 |
| — | New e-bus price | €615k standard / €800k articulated | BRIEF + WEB | Brief §4.5; matches EMT's Mar 2026 award (Irizar 50 for €30.75M; Solaris 30 artic. for €24M) |
| — | CO₂ factors | CNG 2.7175 kg/kg; grid 108.4 g/kWh | WEB | MITECO inventory; Red Eléctrica 2025 |
| A1 | Bus life | 12 years | DATA | Median age at retirement in EMT's register (CNG 12.7; 2023–25 about 12) |
| A2 | Resale of a retired CNG bus | €10k | WEB | EMT sold 2 to Toledo for €15k each ([nexotrans](https://nexotrans.com/empresa-municipal-de-transportes-de-madrid-vende-dos-autobuses-de-gnc-a-la-diputacion-de-toledo/)); European listings €3–7k ([truckscout24](https://www.truckscout24.com/tsp/ts-218-08-768)) |
| A3 | Book value of a CNG bus | €291k, written off over 12 years | WEB + CALC | €151.5M ÷ 520 buses, 2021 tender ([EMT](https://www.emtmadrid.es/Noticias/EMT-invierte-177-millones-en-la-compra-de-520-auto.aspx)) |
| A4 | Most new buses a year | 380 | DATA | EMT's record intake (382 in 2018, 354 in 2022), from the register |
| A5 | Gas contract penalty | none (base); 80 % take-or-pay as a test | ASSUMPTION | Tender documents not readable; volumes from [elEconomista](https://www.eleconomista.es/energia/noticias/14026766/11/26/la-emt-de-madrid-licita-136-millones-para-suministrar-biometano-a-sus-autobuses.html) and the [Madrid portal](https://contratacion.madrid.es/en-licitacion/) |
| A6 | Grid upgrade, order to energised | 3 years | WEB | European studies say 12–36 months ([T&E](https://transportenvironment.org/uploads/files/1-TE_truck-depot-charging_final-report_v15.3.pdf), [ZEMO](https://www.zemo.org.uk/assets/reports/ZEMO_ZERO_EMISSION_BUS_GUIDE_2022_ONLINE_VERSION.pdf)). The Almería 20 MVA substation tender allows 25 months to commission ([El Estrecho](https://www.elestrechodigital.com/2026/11/10/el-puerto-de-almeria-licita-por-127-millones-una-nueva-subestacion-electrica-para-ampliar-su-capacidad-industrial)). Plus saturated nodes in Madrid |
| A7 | Grid upgrade cost per depot | €5M flat | WEB, rounded | 20 MVA substation €2.3M + 66 kV line €11.5M ([Valencia Plaza](https://valenciaplaza.com/valenciaplaza/comarca-y-empresa/una-nueva-subestacion-unira-la-planta-de-helados-de-ferrero-en-alzira-con-la-red-electrica-por-13-millones)); Almería €12.7M; medium-voltage connection €0.4–2M (T&E) |
| A8 | Battery cost | €250/kWh turnkey | WEB | Turnkey LFP €250/kWh up to 2 MWh, €175–200 above 5 MWh ([cubeconcepts](https://cubeconcepts.de/en/battery-storage/cost-roi/)); installed €300–500/kWh for small sites ([pv Europe](https://www.pveurope.eu/solar-storage/october-battery-index-residential-prices-slip-commercial-diverges)) |
| A9 | Battery efficiency / usable share | 88 % / 90 % | ASSUMPTION | Typical LFP values; not searched yet |
| A10 | Charger per bus | €110k pantograph incl. works | DATA (EMT accounts) | Sanchinarro €12.58M ÷ 114 pantographs; plug-in €26k (Entrevías) or €30k ([HSL](https://www.hsl.fi/en/hsl/electric-buses)) |
| A11 | La Elipa | opens 2030, 20 MW, 318 points, €134.3M | WEB | 32-month works contract tendered mid-2026 ([eldiario](https://www.eldiario.es/madrid/somos/ayuntamiento-madrid-renuncia-privatizar-cocheras-emt-elipa-despues-fracasar-primera-licitacion_1_13325166.html), [carrilbus](https://carrilbus.com/emt-madrid-impulsa-la-electrificacion-de-su-flota-con-la-licitacion-de-las-nuevas-cocheras-de-la-elipa)) |
| A12 | CNG-to-electric conversion | not used | WEB | Only diesel conversions are sold, at €300–350k ([Urban Transport Magazine](https://www.urban-transport-magazine.com/en/retrofitting-instead-of-new-built-conversion-from-diesel-to-electric-buses/)) |
| A13 | Grid CO₂ to 2035 | held at 108.4 g/kWh | ASSUMPTION | Conservative; Spain's grid is decarbonising |
| A14 | New orders deliver from 2028; 120 e-buses arrive 2027 | | WEB + ASSUMPTION | EMT's Mar 2026 award delivers Q4 2026 – mid 2027 (9–15 months). Solaris Leipzig: first 15 in H2 2026, rest mid 2027 ([Solaris](https://www.solarisbus.com/en/press/solaris-to-deliver-40-electric-buses-to-leipzig-2341)). Assumes the next tender is awarded in 2027 |
| A15 | Grid and battery orders from 2027 | | ASSUMPTION | Nothing can be ordered before the plan is approved |
| A16 | Battery, order to service | 1 year | WEB, **change proposed** | Internet says **12–24 months** end to end: C&I equipment 8–10 weeks ([howtostoreelectricity](https://howtostoreelectricity.com/1000-battery-storage-questions/)), utility equipment 10–16 months + 5–8 months commissioning, a Belgian 24 MWh project about 1 year ([energy-storage.news](https://www.energy-storage.news/eu-roundup-700mwh-of-bess-projects-move-forward-in-germany-belgium-france-finland-latvia-and-portugal/)), permits and grid add a year or more in France ([globallawexperts](https://globallawexperts.com/news/battery-storage-projects-france)). **Proposal: 2 years (ready 2029)**, 1 year as the optimistic case |
| A17 | Night charging power today | Carabanchel 10, Sanchinarro 8, Entrevías 1 MW; Fuencarral = its current use (2.0 MW); La Elipa 0 until it opens | WEB + CALC | Carabanchel 10 MVA transformers ([espormadrid](https://www.espormadrid.es/2024/08/320-puntos-de-recarga-para-autobuses.html)); Sanchinarro 8 MW main + 5 MW backup (madrid.es press note); Entrevías 10 chargers × 100 kW (EMT accounts); Fuencarral unknown, so calculated from its 7 electric lines |
| A18 | Free charging points today | Sanchinarro 120, Entrevías 10, others 0 | WEB + CALC | Sanchinarro 134 points minus about 13 buses in use; Carabanchel's 320 already serve its about 360 e-buses |
| A19 | Fast charger for over-range lines | €350k per line | WEB | [HSL](https://www.hsl.fi/en/hsl/electric-buses): quick charger €350k |
| — | Natural gas energy content | 14.6 kWh/kg | ASSUMPTION | Typical higher heating value; only used to compare with the tender's GWh. Not searched yet |
| — | Buses owned per peak bus | 1.102 | CALC | 2,210 fleet ÷ 2,005 peak buses; each line needs peak × 1.102 buses |

## 3. Year-by-year columns (`results/years.csv`, one row per scenario and year)

| Column | What it is | How it is calculated | Built on |
|---|---|---|---|
| `delivered` | New buses arriving that year | The scenario's request, capped at A4 (380). 2026–27 only the 120 already ordered (A14) | Scenario + A4 + A14 |
| `renewals` | Electric buses replaced because they reached 12 years | Count of BEV/H₂ with age ≥ A1, replaced first, like for like | DATA + A1 |
| `new_ze` | Buses that add to the electric fleet | delivered − renewals | CALC |
| `n_ze`, `n_cng`, `fleet_total` | Fleet by technology at year end | Starting fleet + new − retired. Fleet can rise above 2,210 while bought buses wait for power | CALC |
| `ze_share_pct` | Zero-emission share (File 4 definition) | 100 × n_ze ÷ fleet_total | CALC |
| `lines_electric` | Lines fully electric | A line converts when the pool has its buses (peak × 1.102) **and** its depot has night power left. Order: most km per bus first (most CO₂ per bus); over-range lines last | CALC + depot power |
| `km_share_electric_pct` | Share of daily km run electric | Converted lines' km ÷ 339,220 | CALC |
| `idle_ze` | Electric buses bought but not running | Pool left after converting whole lines; usually caused by depot power | CALC |
| `cng_retired` | Gas buses taken out | Same number as the buses a converted line receives, oldest first | CALC |
| `early_scrapped` | Gas buses retired before 12 years | Retired buses with age < A1 | CALC + A1 |
| `cng_over_life` | Gas buses still running past 12 years | Age > A1 and not yet retired | CALC + A1 |
| `electricity_mwh` | Grid electricity | Σ electric lines: km × 365 × kWh/km ÷ 0.90 | BRIEF factors |
| `gas_gwh`, `cng_t` | Gas burned | Σ gas lines: km × 365 × kg/km (× 14.6 kWh/kg for GWh) | BRIEF + gas energy assumption |
| `gas_tender_gwh` | Contracted volume | 583 GWh a year for 2027–29 (1,750 ÷ 3) | WEB (tender) |
| `co2_t` | Tailpipe CO₂ (CNG) + grid CO₂ (electricity) | CNG kg × 2.7175 + electric kWh × 108.4 g | BRIEF + WEB factors |
| `co2_avoided_t` | Against 2025 frozen | CO₂ if the 2025 network ran unchanged − co2_t | CALC (File 4 rule) |
| `capex_buses_meur` | Bus purchases | delivered × €615k, + €185k for each articulated gas bus replaced | BRIEF prices |
| `capex_chargers_meur` | Chargers | Buses on converted lines beyond free points (A18) × €110k, + €350k per over-range line | A10, A18, A19 |
| `capex_grid_meur` | Grid upgrades | €5M per depot that needs more power at 100 %, charged in the order year (2027) | A7, A15 |
| `capex_bess_meur` | Batteries | Nameplate MWh × €250/kWh, in the order year | A8, A9 |
| `capex_la_elipa_meur` | La Elipa works | €134.3M spread over the 3 years before opening; **the same in every scenario** | WEB |
| `capex_total_meur` | Sum of the five capex columns | | CALC |
| `stranded_meur` | Book value lost on early-scrapped buses | €291k × (12 − age) ÷ 12 per bus. **Not added to capex**: it is an accounting loss, not cash | A3 |
| `resale_meur` | Money back from selling retired buses | retired × €10k. **Not subtracted from capex** yet | A2 |
| `take_or_pay_meur` | Gas paid for but not used | max(0, share × 583 − gas used) × €58.1/MWh in 2027–29; 0 in the base case | A5 + WEB price |
| `blocked_depots` | Depots that stopped a line converting that year | Line's night energy > depot capacity | CALC |

**Depot power, how it works:**
- Capacity = MW × 7 h.
  - **Grid:** an upgrade adds the MW missing for 100 % from its ready year (2027 + A6 = 2030).
  - **Battery:** it adds (100 % need − today's MW × 7) of night energy from its ready year (2027 + A16).
- **A battery can only be recharged by the depot's own connection during the day:**
  - The most it can deliver is today's MW × 17 h × 0.88.
  - At Fuencarral (2 MW) and Entrevías (1 MW) that is far short of what they need. This is why "batteries only" stalls.

## 4. Summary columns (`results/summary.csv`, one row per scenario)

| Column | Meaning |
|---|---|
| `ze_100_year` | First year with no gas buses **and** every line electric |
| `ze_pct_2030`, `ze_pct_2035` | Zero-emission share in those years |
| `buses_bought`, `peak_intake` | Total buses delivered 2026–35, and the busiest year |
| `early_scrapped` | Gas buses retired before 12 years, total |
| `max_cng_over_life` | Most gas buses running past 12 years in any year |
| `max_idle_ze` | Most electric buses waiting for power in any year |
| `capex_meur` and its parts | Capital spending 2026–35, constant 2025 €, excl. VAT |
| `stranded_meur`, `resale_meur`, `take_or_pay_meur` | Shown apart from capex (see above) |
| `gas_2027_29_gwh` | Gas used during the tender period, against 1,750 GWh |
| `co2_2035_t`, `co2_avoided_kt` | CO₂ in 2035; total avoided 2026–35 |
| `eur_per_t_avoided` | Capex ÷ CO₂ avoided. **Capital only, no running costs**, so it overstates the cost |
| `binding` | What stops the scenario reaching 100 % by 2035 |

## 5. Each scenario (row), and how its purchases are set

| Scenario | Buses wanted each year | Depot power | What it tests |
|---|---|---|---|
| S0 current pace | renewals + 77 | Grid upgrades | Brief S0: the 2021–25 pace (77.2 a year, notebook 01 §3) |
| S1 2030, grid only | renewals + (buses still needed ÷ years left to 2030) | Grid upgrades only | Brief S1, waiting for the grid |
| S1 2030, batteries + grid | same | Batteries bridge until the grid arrives | Brief S1 with a bridge |
| Fastest, batteries + grid | renewals + everything still needed | Batteries + grid | Speed limit. **Same result as S1 today**, because both hit 380 a year |
| Target 2032, batteries + grid | renewals + (still needed ÷ years left to 2032) | Batteries + grid | A smoother path |
| Replace at 12 years, grid | renewals + gas buses reaching 12 that year | Grid upgrades | No early scrapping |
| Replace at 12 years, batteries only | same | Batteries only | Can batteries avoid grid works? |

## 6. Simplifications to know about
- **Conversion timing:** a line converted in a year counts as electric for that whole year. This flatters CO₂ in fast years.
- **Bus types:** the line table marks only line 34 as articulated, but the fleet has 85 articulated buses. Energy uses the line types; prices use the retired buses' types.
- **Grid upgrades:** one per depot, sized to 100 % and costed at a flat €5M. Batteries are sized once, for 100 %.
- **Depot assignments** come from old records (P). Today La Elipa's lines run from Fuencarral, and the model keeps them there until 2030.
- **Not included:** running costs, discounting, inflation, daytime top-up energy, hydrogen beyond line 145, staff and space.

## 7. Proposed additions (to discuss)

### Columns
| Proposed column | Why | Data we have / need |
|---|---|---|
| **Capex per year vs EMT's investment capacity** | Fast plans need €250–330M a year. EMT invested €52.7M in 2025 against €887M of income (2025 accounts) | Have: 2025 accounts (handoff). Need: municipal budget and EU funds |
| **Running costs (opex)**: electricity vs biomethane per km, maintenance | Electric buses are cheaper to run. This could reverse the cost ranking of fast vs slow plans | Have: tender gas price €58/MWh, 6.1TD tariff, OMIE prices. Need: maintenance €/km (web) |
| **Net cost** = capex + book value lost − resale + take-or-pay − opex savings | One comparable cost figure per scenario | From the columns above |
| **Cost discounted (NPV)** | €1 in 2026 is worth more than €1 in 2034 | Need: discount rate (assumption) |
| **Peak MW per depot per year** | Shows when each depot hits its limit | Model already has it; just output it |
| **Battery replacement for e-buses** (around year 7–8) | A real mid-life cost | Need: pack price (web) |
| **Lifecycle CO₂** (making a new bus vs keeping an old one) | Scrapping young buses early wastes their embodied CO₂ | Need: embodied CO₂ per bus (web) |
| **NOx / air quality**, riders on electric lines | The political case; ridership is in our data | Have: ridership by line (EMT open data) |
| **Funding and grants** | La Elipa (CEF) and Sanchinarro (€4.69M EU) already use them | Need: CEF, PRTR, Next Generation EU amounts (web) |

### Scenarios (rows)
| Proposed scenario | Question it answers |
|---|---|
| **2030, "what it would take"**: deliveries from 2027 + 450 a year | The only combination that reaches 2030. What does it cost and require? |
| **Budget-capped** (for example €150M or €200M a year) | When do we finish if money is the limit? |
| **Gas-contract aligned**: run the full gas fleet through 2029, then sprint | Cost of honouring the tender as written |
| **Depot by depot** (Sanchinarro first, then Carabanchel…) | Is it cheaper to finish one depot at a time than to spread purchases? |
| **Hydrogen for the 6 over-range lines** (the handoff's option) | H₂ against terminal fast chargers |
| **Flexible grid access + batteries** (CNMC Jul 2026 permits) | Can a smaller, faster connection plus batteries replace a full upgrade? |
| **La Elipa late** (2031–32) or early (2029) | How much depends on La Elipa? |
| **Bus life 14 years** | Fewer purchases, more gas, less scrapping |
| **Battery 2-year lead (A16 corrected)** | Does the bridge still work? |

## 8. Columns added on 21 Nov 2026 (and their sources)

| Column | Calculation | Source of inputs |
|---|---|---|
| `riders_ze_lines_pct` | Working-day riders on electric lines ÷ all riders | DATA: EMT ridership 2026 (average of working days in EMT's calendar) |
| `opex_energy_meur` | Electricity MWh × €85 + gas MWh × €58.1 + H₂ kg × €12 | WEB: electricity 60–90 €/MWh at night + 1.6 €/MWh regulated tolls and charges (CNMC/MITECO 2026); gas from the tender; H₂ €10–15/kg (atawey, CleanTechnica) |
| `opex_maint_meur` | km × €0.19 (CNG) or €0.087 (electric) | WEB: [Seville study, Energy 2025](https://www.sciencedirect.com/science/article/pii/S0360544225026672) |
| `capex_battery_swaps_meur` | E-buses reaching 8 years × €100k | WEB: vendor blogs, €75–110k per pack (weak source) |
| `embodied_new_t` / `embodied_wasted_t` | New buses × 155 t; early-scrapped gas buses × 108 t × remaining life share | WEB: [Trondheim LCA](https://www.mdpi.com/1996-1073/14/3/770): e-bus +47 t vs conventional, battery ~48 t |
| `nox_t` | Gas km × 0.6 g/km | WEB: [MDPI Atmosphere 2025](https://www.mdpi.com/2073-4433/16/3/293), Euro VI CNG |
| `capex_h2_meur` | (€640k − €615k) per H₂ bus + €10.86M per extra station (432 kg/day) | WEB: EMT tender 2022, Entrevías station (18 kg/h) |
| `grants_meur` | Infrastructure capex × grant share (0 in base) | Sanchinarro got €4.69M of €12.58M (37 %) |
| `emt_invest_ref_meur`, `capex_over_emt_invest` | Yearly capex ÷ EMT's investment budget (2026: €135.3M; 2027 and later: €167.2M) | WEB: [EMT 2026 budget](https://www.emtmadrid.es/Noticias/El-presupuesto-de-EMT-Madrid-para-2026-rozara-los.aspx), [2027 budget](https://www.madridesnoticia.es/2026/10/flota-de-emt-autobuses-electricos/) |
| `fleet_value_2035_meur` | Every bus left in 2035 at straight-line value (BEV €615k, H₂ €640k, CNG €291k over 12 years) | CALC |
| `net_cost_meur` | capex + opex + gas penalty − resale − fleet value 2035 | CALC |
| `npv_meur` | Same, discounted at 3 % to 2026 | WEB: EC appraisal guidance 3–5 % |
| `peak_mw` per depot per year (`depot_years.csv`) | Night load of the depot's electric lines ÷ 7 h, against capacity | CALC |
| Flexible grid access | Connection in 2 years for €2M instead of 3 years for €5M | WEB: [CNMC resolution, Jul 2026](https://www.cnmc.es/prensa/permisos-acceso-flexibles-20260811); the 2-year / €2M values are an assumption |

## 9. Corrections on 21 Nov 2026 (after the user flagged the current-pace years)
| Change | Why | Source |
|---|---|---|
| **A1b Maximum bus age 16 years**: a gas bus reaching 16 is replaced by an electric bus | Current pace kept 2023 buses running until 2053 (30 years) | DATA: EMT register, 99 % of buses retired by 16.4 years, max 17.2 |
| **Horizon to 2040**; money and CO₂ still counted for 2026–2035 | The 100 % year was extrapolated outside the model | CALC |
| **A31 Buses delivered only when a depot can charge them** (`deferred_for_power` column) | Up to 673 buses were bought and parked | CALC (planning rule) |
| **A14 update: 70 of the 120 e-buses in 2026, 50 in 2027** | All 120 were placed in 2027 | WEB: EMT 2026 budget, 70 e-buses (€47.7M) |
| **Rounding fix on the last line** | 2 gas buses were left until age 16 | CALC |
| **New scenario B9 "all-in now"**: power ordered Dec 2026 | Needed to reach 2030 once buses wait for power | Plan search |
| `scenarios/checks.py`: 14 consistency checks | Fleet identity, shares, capex sums, ages, idle buses, CO₂ at 100 % | CALC |
