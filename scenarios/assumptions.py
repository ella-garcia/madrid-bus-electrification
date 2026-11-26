"""Every scenario input in one place. Source types: DATA (our datasets), WEB (internet, link in
notes/scenario-model-explained.md), BRIEF, CALC, ASSUMPTION.

Approved by the user: A1-A13 on 20 Nov 2026, A14-A30 on 21 Nov 2026.
Change a value here, or override it per scenario in scenarios.py.
"""

BASE = dict(
    # --- Brief, fixed (section 4.5) ---------------------------------------------------------------
    kwh_km={"Standard": 1.30, "Articulated": 1.85},          # BRIEF
    range_km={"Standard": 300, "Articulated": 240},          # BRIEF
    cng_kg_km={"Standard": 0.45, "Articulated": 0.65},       # BRIEF
    charge_eff=0.90,                                          # BRIEF
    window_h=7,                                               # BRIEF, 23:00-06:00
    bus_price={"Standard": 615_000, "Articulated": 800_000},  # BRIEF / WEB EMT Mar 2026 award
    cng_kgco2_per_kg=2.7175,                                  # WEB MITECO
    service_days=365,                                         # BRIEF

    # --- Approved assumptions --------------------------------------------------------------------
    bus_life=12,                 # A1  DATA EMT median retirement age (fleet register)
    max_age=16,                  # A1b DATA 99 % of EMT buses retired by 16.4 years (2015-25); gas buses must go by 16
    resale_eur=10_000,           # A2  WEB  Toledo sale ~15k, market 3-7k
    cng_book_price=291_000,      # A3  WEB  151.5M / 520 buses (2021 tender), straight-line over bus_life
    max_intake=380,              # A4  DATA EMT record year (2018)
    gas_take_or_pay=0.0,         # A5  ASSUMPTION 0 = volumes follow the fleet; 0.8 = pay for 80 % of tender
    grid_lead_years=3,           # A6  WEB  12-36 months in European studies
    grid_upgrade_eur=5_000_000,  # A7  WEB  substation 2.3M; with 66 kV line 12.7-13.9M
    bess_eur_kwh=250,            # A8  WEB  turnkey LFP benchmark
    bess_rt_eff=0.88,            # A9  ASSUMPTION
    bess_dod=0.90,               # A9  ASSUMPTION
    charger_eur=110_000,         # A10 DATA Sanchinarro 12.58M / 114 pantographs
    la_elipa_open=2030,          # A11 WEB  32-month works contract re-tendered mid-2026
    la_elipa_mw=20,              # A11 WEB
    la_elipa_points=318,         # A11 WEB
    la_elipa_capex_eur=134_300_000,  # WEB works contract excl. VAT (in every scenario)
    retrofit=False,              # A12 WEB  no CNG-to-electric offer found
    grid_gco2_kwh=108.4,         # A13 WEB  Red Electrica 2025, held flat

    # --- Approved 21 Nov 2026 -------------------------------------------------------
    first_order_delivery=2028,   # A14 WEB+ASSUMPTION Mar 2026 award delivered in 9-15 months
    order_2026={2026: 70, 2027: 50},  # A14 WEB  120 e-buses awarded Mar 2026; EMT 2026 budget includes 70
    decision_year=2027,          # A15 ASSUMPTION
    bess_lead_years=1,           # A16 WEB  12-24 months end to end (1 = optimistic; scenario tests 2)
    depot_mw_today={"Fuencarral": None, "Carabanchel": 10.0, "Sanchinarro": 8.0, "Entrevias": 1.0, "La Elipa": 0.0},  # A17
    depot_points_today={"Fuencarral": 0, "Carabanchel": 0, "Sanchinarro": 120, "Entrevias": 10, "La Elipa": 0},       # A18
    opp_charger_eur=350_000,     # A19 WEB  HSL quick charger
    gas_kwh_per_kg=14.6,         # A20 ASSUMPTION typical natural-gas higher heating value
    gas_tender_gwh_yr={2027: 583, 2028: 583, 2029: 583},  # WEB 1,750 GWh over 2027-29
    gas_price_eur_mwh=58.1,      # CALC 101.69M / 1,750 GWh, incl. taxes (tender)
    elec_price_eur_mwh=85.0,     # A21 WEB  night energy 60-90 EUR/MWh + regulated 1.6 EUR/MWh + tax
    maint_eur_km={"CNG": 0.19, "BEV": 0.087, "H2": 0.19},  # A22 WEB Seville study 2025 (H2 = CNG, assumption)
    bev_battery_swap_age=8,      # A23 WEB  typical warranty / mid-life
    bev_battery_swap_eur=100_000,  # A23 WEB  75-110k per pack (vendor blogs)
    embodied_t={"CNG": 108, "BEV": 155},  # A24 WEB Trondheim LCA: e-bus +47 t vs conventional; battery ~48 t
    nox_g_km_cng=0.6,            # A25 WEB  Euro VI CNG urban bus (MDPI Atmosphere 2025)
    discount_rate=0.03,          # A26 WEB  EC appraisal guidance 3-5 %
    emt_invest_meur={2026: 135.3, 2027: 167.2},  # A27 WEB EMT budgets: total investment (all purposes)
    budget_cap_meur=None,        # A27 scenario lever: max yearly spend on buses + chargers + power
    over_range_tech="BEV",       # A28 "BEV" (terminal fast charger) or "H2"
    h2_bus_eur=640_000,          # A28 WEB  EMT 2022 tender up to 640k
    h2_station_eur=10_860_000,   # A28 WEB  Entrevias station
    h2_station_kg_day=432,       # A28 WEB  18 kg/h x 24 h
    h2_kg_100km=7.5,             # A28 WEB  JIVE 2 average 7.49
    h2_price_eur_kg=12.0,        # A28 WEB  10-15 EUR/kg delivered
    grant_share_infra=0.0,       # A29 ASSUMPTION EU grants on chargers/grid/batteries (Sanchinarro got 37 %)
    power_aware=True,            # A31 CALC buses are only delivered when a depot can charge them (forced replacements excepted)
    flexible_access=False,       # A30 WEB  CNMC Jul 2026 flexible permits: modelled as 2-year, 2M connection
)

LABELS = {
    "A1": "CNG bus life 12 years (replacement age)", "A1b": "Maximum bus age 16 years (forced replacement)", "A2": "Resale EUR 10k", "A3": "CNG book value EUR 291k over 12 years",
    "A4": "Max 380 new buses a year", "A5": "Gas volumes follow the fleet (no take-or-pay)",
    "A6": "Grid upgrade 3 years", "A7": "Grid upgrade EUR 5M per depot", "A8": "Battery EUR 250/kWh",
    "A9": "Battery 88 % round trip, 90 % usable", "A10": "Pantograph EUR 110k", "A11": "La Elipa opens 2030 (20 MW, 318 points)",
    "A12": "No CNG retrofit", "A13": "Grid CO2 held at 108.4 g/kWh",
    "A14": "New orders deliver from 2028; the 120 e-buses arrive 70 in 2026, 50 in 2027", "A15": "Grid/battery orders from 2027",
    "A16": "Battery 1 year to install (web: 12-24 months)", "A17": "Depot power today: Carabanchel 10, Sanchinarro 8, Entrevias 1 MW, Fuencarral = current use",
    "A18": "Free charging points today: Sanchinarro 120, Entrevias 10, others 0", "A19": "Terminal fast charger EUR 350k per above-range line",
    "A20": "Gas 14.6 kWh/kg", "A21": "Electricity EUR 85/MWh all-in", "A22": "Maintenance CNG 0.19, electric 0.087 EUR/km",
    "A23": "E-bus battery swap at 8 years, EUR 100k", "A24": "Embodied CO2: CNG bus 108 t, e-bus 155 t",
    "A25": "CNG NOx 0.6 g/km", "A26": "Discount rate 3 %", "A27": "EMT investment 2026 EUR 135M, 2027 EUR 167M",
    "A28": "Hydrogen: bus 640k, station 10.9M per 432 kg/day, 7.5 kg/100 km, EUR 12/kg",
    "A29": "No EU grants in base", "A30": "Flexible grid access: 2 years, EUR 2M per depot", "A31": "Buses delivered only when a depot can charge them",
}
