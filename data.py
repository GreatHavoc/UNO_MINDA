"""
data.py
=======
Static business intelligence data for UNO Minda Limited.
Shared by both the CLI (uno_minda_intelligence.py) and the API server (server.py).
"""

UNO_MINDA_PROFILE = {
    "company_name": "UNO Minda Limited",
    "former_name": "Minda Industries Limited",
    "founded": "1958",
    "headquarters": "Gurugram, Haryana, India",
    "chairman": "N.K. Minda",
    "stock_exchange": "NSE: UNOMINDA | BSE: 532539",
    "market_cap_approx": "INR 36,000+ Crore",
    "revenue_fy25": "INR 16,804 Crore (up 19.5% YoY)",
    "revenue_fy24": "INR 14,065 Crore",
    "ebitda_fy25": "INR 1,885 Crore (up 18% YoY)",
    "pat_fy25": "INR 930 Crore",
    "employees": "20,000+",
    "manufacturing_plants": "60+ plants across India, Indonesia, Vietnam, Mexico",
    "r_and_d_centers": "5 (Manesar, Pune, Chennai, Bengaluru, Japan)",
    "tier": "Tier-1 Automotive Supplier",
    "oem_customers": "500+ Indian and International OEMs",
    "product_lines": 26,
    "website": "https://www.unominda.com",
}

PRODUCT_PORTFOLIO = {
    "Switching Systems": {
        "segments": ["2-Wheeler", "3-Wheeler", "4-Wheeler", "Off-road", "Commercial Vehicles"],
        "market_position": "India's #1 switch player",
        "products": [
            "Ignition switches", "Combination switches", "Handle bar switches",
            "Push button switches", "Gear shift switches", "Door latch switches"
        ],
    },
    "Automotive Lighting": {
        "segments": ["2-Wheeler", "3-Wheeler", "4-Wheeler"],
        "market_position": "Leading lighting supplier in India",
        "products": [
            "Head lamps", "Tail lamps", "LED blinkers", "DRLs (Daytime Running Lights)",
            "Fog lamps", "Interior lighting", "LED projection headlamps"
        ],
    },
    "Alloy Wheels": {
        "segments": ["2-Wheeler", "4-Wheeler"],
        "market_position": "#1 in PV alloy wheels in India",
        "products": [
            "Diamond-cut alloy wheels", "Painted alloy wheels",
            "Gun-metal machined wheels", "Lightweight alloy wheels"
        ],
    },
    "Acoustics (Horns)": {
        "segments": ["2-Wheeler", "3-Wheeler", "4-Wheeler", "Commercial Vehicles"],
        "market_position": "Market leader in automotive horns",
        "products": [
            "Electric horns", "Air horns", "Disc horns",
            "Windtone horns", "Multi-tone horns"
        ],
    },
    "Seating Systems": {
        "segments": ["2-Wheeler", "3-Wheeler", "4-Wheeler"],
        "market_position": "Major seating supplier",
        "products": [
            "Driver seats", "Passenger seats", "Rear seats",
            "Seat frames", "Seat adjusters"
        ],
    },
    "Casting": {
        "segments": ["4-Wheeler", "Commercial Vehicles"],
        "market_position": "Growing die-casting division",
        "products": [
            "Aluminum die-cast components", "Engine parts",
            "Transmission housings", "Structural castings"
        ],
    },
    "Sensors & Controllers": {
        "segments": ["2-Wheeler", "4-Wheeler", "EV"],
        "market_position": "Fast-growing electronics segment",
        "products": [
            "Speed sensors (contact & non-contact)", "Temperature sensors",
            "Pressure sensors", "Head lamp levelling sensors",
            "Electronic controllers", "EV battery management sensors"
        ],
    },
    "EV-Specific Products": {
        "segments": ["2-Wheeler EV", "3-Wheeler EV", "4-Wheeler EV"],
        "market_position": "Emerging EV component leader",
        "products": [
            "Electric Drive Units (EDU)", "Dedicated Hybrid Transmissions",
            "Acoustic Vehicle Alert Systems (AVAS)", "EV controllers",
            "Battery management components", "On-board chargers",
            "CCS2 charging inlets", "EV motor controllers"
        ],
    },
    "ADAS": {
        "segments": ["4-Wheeler"],
        "market_position": "Entry stage with growth plans",
        "products": [
            "Advanced Driver Assistance Systems",
            "Sensor integration modules",
            "ADAS controllers"
        ],
    },
    "Sunroofs": {
        "segments": ["4-Wheeler Premium"],
        "market_position": "New entrant - facility commissioning by FY27",
        "products": [
            "Panoramic sunroofs", "Standard sunroofs"
        ],
    },
    "Rear View Mirrors (4W)": {
        "segments": ["4-Wheeler"],
        "market_position": "Launched March 2024",
        "products": [
            "Manual mirrors", "Electric adjustable mirrors",
            "Auto-dimming mirrors"
        ],
    },
    "Alternate Fuel Systems": {
        "segments": ["4-Wheeler", "Commercial Vehicles"],
        "market_position": "Partnership with Westport Fuel Systems",
        "products": [
            "CNG fuel systems", "LPG fuel systems",
            "Alternate fuel components"
        ],
    },
}

COMPETITORS = {
    "indian": {
        "Bosch Ltd (India)": {
            "ticker": "BOSCHLTD.NS",
            "headquarters": "Bengaluru, India",
            "revenue_approx": "INR 14,000+ Crore (India ops)",
            "key_products": [
                "Fuel injection systems", "Automotive electronics",
                "Braking systems", "Steering systems", "Diagnostics"
            ],
            "competition_areas": [
                "Sensors", "Controllers", "Automotive electronics",
                "ADAS", "Lighting (indirect)"
            ],
            "market_position": "India's largest auto component company; Global #1 Tier-1",
            "strength": "Deep technology portfolio, strong brand, R&D leadership",
        },
        "Samvardhana Motherson International Ltd": {
            "ticker": "MOTHERSON.NS",
            "headquarters": "Noida, India",
            "revenue_approx": "INR 90,000+ Crore (consolidated)",
            "key_products": [
                "Wiring harnesses", "Mirror systems", "Polymer modules",
                "Metal modules", "Vision systems", "Seating"
            ],
            "competition_areas": [
                "Seating", "Rear view mirrors", "Lighting (via Samvardhana Motherson Reflectec)",
                "Alloy wheels (indirect)", "Casting"
            ],
            "market_position": "India's 2nd largest auto component company; Global Top 20",
            "strength": "Massive global scale, 400+ facilities, diversified portfolio",
        },
        "Tube Investments of India Ltd (TII)": {
            "ticker": "TIINDIA.NS",
            "headquarters": "Chennai, India",
            "revenue_approx": "INR 16,000+ Crore",
            "key_products": [
                "Bicycle components", "Steel strips", "Metal-formed products",
                "Chains", "Tubes"
            ],
            "competition_areas": [
                "Casting (TII's CG Power acquisition in EV space)",
                "Alloy wheels (indirect competition)"
            ],
            "market_position": "Diversified industrial, growing in auto via CG Power",
            "strength": "Murugappa Group backing, strong in EV motor/controllers via CG Power",
        },
        "Motherson Sumi Wiring India Ltd": {
            "ticker": "MSUMI.NS",
            "headquarters": "Noida, India",
            "revenue_approx": "INR 20,000+ Crore",
            "key_products": [
                "Wiring harnesses", "Cab assemblies"
            ],
            "competition_areas": [
                "EV controllers (indirect)", "Electronics content"
            ],
            "market_position": "India's largest wiring harness manufacturer",
            "strength": "Dominant in wiring harness, key for EV architecture",
        },
        "Endurance Technologies Ltd": {
            "ticker": "ENDURANCE.NS",
            "headquarters": "Aurangabad, India",
            "revenue_approx": "INR 9,000+ Crore",
            "key_products": [
                "Aluminium die-casting", "Suspension systems",
                "Braking systems", "Transmission components"
            ],
            "competition_areas": [
                "Casting (die-casting)", "Alloy wheels (indirect)",
                "Suspension components"
            ],
            "market_position": "Major die-casting player, strong in 2W/3W",
            "strength": "Strong in aluminium casting, growing EV presence",
        },
        "Suprajit Engineering Ltd": {
            "ticker": "SUPRAJIT.NS",
            "headquarters": "Bengaluru, India",
            "revenue_approx": "INR 3,000+ Crore",
            "key_products": [
                "Automotive cables", "Speedometers", "Instrument clusters",
                "LED lighting", "Switches"
            ],
            "competition_areas": [
                "Switches", "Lighting (LED)", "Sensors"
            ],
            "market_position": "Global leader in automotive cables; growing in switches/lighting",
            "strength": "Strong M&A strategy, global cable leadership",
        },
        "Gabriel India Ltd": {
            "ticker": "GABRIEL.NS",
            "headquarters": "Pune, India",
            "revenue_approx": "INR 2,500+ Crore",
            "key_products": [
                "Shock absorbers", "Ride control products",
                "Suspension systems"
            ],
            "competition_areas": [
                "Seating (ride comfort components)", "Aftermarket"
            ],
            "market_position": "India's leading shock absorber manufacturer",
            "strength": "Strong aftermarket presence, ANAND Group synergies",
        },
        "Lumax Industries Ltd": {
            "ticker": "LUMAXIND.NS",
            "headquarters": "New Delhi, India",
            "revenue_approx": "INR 2,500+ Crore",
            "key_products": [
                "Automotive lighting", "Rear view mirrors",
                "Gear shifters"
            ],
            "competition_areas": [
                "Lighting (direct)", "Rear view mirrors"
            ],
            "market_position": "Major lighting player (JV with Stanley Electric, Japan)",
            "strength": "Stanley Electric technology backing, strong OEM relationships",
        },
    },
    "global": {
        "Robert Bosch GmbH (Germany)": {
            "ticker": None,
            "headquarters": "Gerlingen, Germany",
            "revenue_approx": "EUR 55+ Billion (global)",
            "key_products": [
                "Fuel injection", "ADAS", "Automotive electronics",
                "Sensors", "Steering", "Braking", "Power tools"
            ],
            "competition_areas": [
                "Sensors", "Controllers", "ADAS", "Automotive electronics",
                "Lighting"
            ],
            "market_position": "World's #1 automotive supplier",
            "strength": "Unmatched R&D budget (EUR 7B+), global reach, technology leadership",
        },
        "Denso Corporation (Japan)": {
            "ticker": None,
            "headquarters": "Kariya, Japan",
            "revenue_approx": "JPY 6+ Trillion (global)",
            "key_products": [
                "Thermal systems", "Powertrain", "Sensors",
                "Electronics", "ADAS", "Instrument clusters"
            ],
            "competition_areas": [
                "Sensors", "Controllers", "EV components",
                "Thermal management"
            ],
            "market_position": "World's #2 automotive supplier",
            "strength": "Toyota group affiliation, thermal management leader",
        },
        "Continental AG (Germany)": {
            "ticker": None,
            "headquarters": "Hanover, Germany",
            "revenue_approx": "EUR 40+ Billion (global)",
            "key_products": [
                "Tires", "ADAS", "Automotive electronics",
                "Powertrain", "Interior solutions"
            ],
            "competition_areas": [
                "ADAS", "Sensors", "Controllers", "Interior electronics",
                "Lighting (indirect)"
            ],
            "market_position": "World's #3-4 automotive supplier",
            "strength": "ADAS leadership, interior electronics dominance",
        },
        "Magna International (Canada)": {
            "ticker": "MGA",
            "headquarters": "Aurora, Canada",
            "revenue_approx": "USD 42+ Billion (global)",
            "key_products": [
                "Body/chassis", "Seating", "Powertrain",
                "Vision systems", "Complete vehicle assembly"
            ],
            "competition_areas": [
                "Seating", "Mirrors/vision systems",
                "Alloy wheels (via global supply chain)", "Casting"
            ],
            "market_position": "World's #4-5 automotive supplier",
            "strength": "Complete vehicle capability, massive global footprint",
        },
        "ZF Friedrichshafen AG (Germany)": {
            "ticker": None,
            "headquarters": "Friedrichshafen, Germany",
            "revenue_approx": "EUR 45+ Billion (global)",
            "key_products": [
                "Transmissions", "Chassis", "ADAS",
                "Active/passive safety", "Electronics"
            ],
            "competition_areas": [
                "ADAS", "Controllers", "EV drivetrain",
                "Active safety"
            ],
            "market_position": "World's #3 automotive supplier",
            "strength": "Transmission/chassis leader, strong in active safety post-WABCO acquisition",
        },
        "Hyundai Mobis (South Korea)": {
            "ticker": None,
            "headquarters": "Seoul, South Korea",
            "revenue_approx": "KRW 50+ Trillion (global)",
            "key_products": [
                "Modules", "Core parts", "Electronics",
                "Lighting", "Braking", "Steering"
            ],
            "competition_areas": [
                "Lighting", "Sensors", "Controllers", "ADAS",
                "Modules"
            ],
            "market_position": "World's #5-6 automotive supplier",
            "strength": "Hyundai/Kia captive business, growing global electronics",
        },
        "Valeo SA (France)": {
            "ticker": None,
            "headquarters": "Paris, France",
            "revenue_approx": "EUR 22+ Billion (global)",
            "key_products": [
                "Lighting", "Visibility systems", "Thermal systems",
                "ADAS", "Electrification"
            ],
            "competition_areas": [
                "Lighting (direct)", "ADAS", "Thermal systems",
                "EV components"
            ],
            "market_position": "Global lighting and thermal leader",
            "strength": "Lighting technology leader, strong EV portfolio, global OEM access",
        },
        "Aptiv PLC (Ireland/USA)": {
            "ticker": "APTV",
            "headquarters": "Dublin, Ireland",
            "revenue_approx": "USD 20+ Billion (global)",
            "key_products": [
                "Signal distribution", "Connectivity", "ADAS",
                "Vehicle architecture", "Active safety"
            ],
            "competition_areas": [
                "ADAS", "Vehicle electronics architecture",
                "Controllers"
            ],
            "market_position": "Global leader in vehicle electronics architecture",
            "strength": "ADAS and connected vehicle architecture leadership",
        },
    },
}

PARTNERSHIPS_AND_JVS = {
    "joint_ventures": {
        "JV with Toyoda Gosei (Japan) & Toyota Tsusho": {
            "entity": "Minda TG Rubber Pvt. Ltd.",
            "equity": "UNO Minda 51%, Toyoda Gosei 44%, Toyota Tsusho 5%",
            "products": "Rubber hoses, steering wheel with airbags, body sealing",
            "status": "Active - Restated JV agreement executed recently (2025)",
            "notes": "Toyoda Gosei merging group companies in India for 'TG One India'",
        },
        "JV with Kosei (Japan)": {
            "entity": "Minda Kosei / Kosei Minda",
            "equity": "Partnership with Kosei Aluminium Co.",
            "products": "Alloy wheels for 2W and 4W",
            "status": "Merged into UNO Minda Ltd (NCLT approved)",
            "notes": "Consolidation completed; strengthens alloy wheel portfolio",
        },
        "JV with Denso Ten (Japan)": {
            "entity": "Minda Denso Ten Ltd.",
            "equity": "Partnership with Denso Ten (Fujitsu Ten / Denso group)",
            "products": "Infotainment, automotive electronics, ECUs",
            "status": "Active",
            "notes": "Key for electronics and infotainment growth",
        },
        "JV with Nabtesco (Japan)": {
            "entity": "Minda Nabtesco",
            "equity": "Partnership with Nabtesco Corporation",
            "products": "Automotive parking brakes",
            "status": "Active",
            "notes": "Serves 4W and CV segments",
        },
        "JV with Kyoraku (Japan)": {
            "entity": "Minda Kyoraku",
            "equity": "Partnership with Kyoraku Co.",
            "products": "Automotive mirrors (2W/3W)",
            "status": "Active",
            "notes": "Strengthens mirror product range",
        },
        "JV with Torica (Japan)": {
            "entity": "Minda Torica",
            "equity": "Partnership with Torica Co.",
            "products": "Automotive locks and keys",
            "status": "Active",
            "notes": "Key for 2W security products",
        },
        "JV with Inovance Automotive (China)": {
            "entity": "Uno Minda Auto Innovations Pvt. Ltd.",
            "equity": "UNO Minda 51%, Inovance Automotive 49%",
            "products": "EV components - Electric Drive Units (EDU), Dedicated Hybrid Transmissions, EV controllers",
            "status": "Signed Feb 17, 2025 - Active",
            "notes": "Major strategic JV for EV growth; technical license agreement from June 2024",
        },
        "JV with Buehler Motor GmbH (Germany) - DISCONTINUED": {
            "entity": "Minda Buehler Motor Ltd.",
            "equity": "Previously joint venture",
            "products": "EV motor/drive systems",
            "status": "UNO Minda acquired full ownership; JV agreement discontinued",
            "notes": "Full acquisition gives complete operational control over EV motor business",
        },
    },
    "strategic_partnerships": {
        "Westport Fuel Systems (Canada)": {
            "type": "Partnership (Alternate Fuel)",
            "details": "Consolidated alternate fuel business in India with Westport Fuel Systems",
            "products": "CNG/LPG fuel systems",
            "status": "Active - Agreements executed to strengthen partnership",
        },
        "Stanley Electric (Japan) - via Lumax": {
            "type": "Technology Partnership (Indirect)",
            "details": "Competitor Lumax has JV with Stanley; UNO Minda competes in lighting",
            "products": "Automotive lighting technology",
            "status": "Competitive dynamic",
        },
    },
    "recent_strategic_moves": {
        "Capex Plan FY25-27": "INR 3,120 Crore across 11 expansion projects",
        "Sunroof Manufacturing": "Facility commissioning by end of FY27 (Jan-Mar 2027)",
        "EV Strategy": "FY27 identified as pivotal year for EV expansion; focus on EDU, AVAS, controllers",
        "Merger of Group Companies": "NCLT approved merger of Minda Kosei, Kosei Minda & Kosei Minda Mould into UNO Minda Ltd",
        "Casting Facility Expansion": "Board approved capex for expansion of casting facility",
        "4W Rear View Mirrors": "Launched in March 2024 - new product segment entry",
        "Plant Visit/Investor Meet": "Plant visit at Manesar facility scheduled June 05, 2026",
    },
}

MARKET_ANALYSIS = {
    "industry_overview": {
        "indian_auto_component_market": "USD 70+ Billion (growing at ~10-12% CAGR)",
        "global_auto_component_market": "USD 2+ Trillion",
        "india_share_in_global_gvc": "~3% (significant growth potential)",
        "key_growth_drivers": [
            "Rising vehicle production in India (PV + 8%, 2W + 5%)",
            "Premiumisation trend - higher content per vehicle",
            "EV transition - new component opportunities",
            "Government push for localization (PLI scheme)",
            "Export opportunities from India as manufacturing hub",
            "Rising electronics content in vehicles",
        ],
    },
    "uno_minda_market_position": {
        "overall_ranking": "Top 3 Tier-1 auto component supplier in India",
        "market_leadership": [
            "#1 in Automotive Switches (all segments)",
            "#1 in PV Alloy Wheels",
            "#1 in Automotive Horns",
            "Leading in 2W Lighting",
            "Strong in Seating Systems",
        ],
        "competitive_advantages": [
            "Broadest product portfolio among Indian Tier-1s (26 product lines)",
            "Deep OEM relationships with 500+ customers",
            "13 JV partnerships providing access to global technology",
            "First-mover advantage in several EV component categories",
            "Strong aftermarket distribution network",
            "Vertically integrated manufacturing (60+ plants)",
            "Growing R&D capability (5 centers, INR 400+ Cr annual spend)",
        ],
        "key_challenges": [
            "Intense competition from global Tier-1s (Bosch, Denso, Continental) in high-tech segments",
            "EV transition risk - some product categories may face disruption",
            "Raw material price volatility (aluminium, copper, plastics)",
            "Dependency on domestic 2W/4W cycles",
            "Need to scale up ADAS and advanced electronics capabilities",
            "Global expansion still limited compared to Motherson/Bosch",
        ],
    },
    "financial_summary": {
        "revenue_cagr_5yr": "~18% CAGR (FY20-FY25)",
        "revenue_fy25": "INR 16,804 Crore (+19.5% YoY)",
        "ebitda_margin_fy25": "~11.2%",
        "pat_fy25": "INR 930 Crore",
        "q2_fy26_revenue_growth": "+13% YoY",
        "q3_fy26_revenue_growth": "+20% YoY at INR 5,018 Crore",
        "q4_fy26_revenue": "INR 5,406 Crore (+17.77% YoY)",
        "debt_equity": "Moderate; improving with strong cash flows",
        "roe_approx": "~14-16%",
        "capex_plan": "INR 3,120 Crore (FY25-27) across 11 projects",
    },
    "swot": {
        "strengths": [
            "Dominant market share in switches, horns, alloy wheels",
            "Diversified product portfolio reducing cyclicality",
            "Strong JV network providing technology access",
            "Established OEM relationships across vehicle segments",
            "Growing aftermarket business",
        ],
        "weaknesses": [
            "Lower margins compared to global peers",
            "Limited presence in high-margin electronics/ADAS",
            "Global revenue share still small vs domestic",
            "Some JVs add complexity in decision-making",
        ],
        "opportunities": [
            "EV component market (EDU, controllers, AVAS) - INR 50,000+ Cr by 2030",
            "ADAS penetration in India from <5% to 30%+ by 2030",
            "Sunroof market growing at 25%+ CAGR",
            "Export growth - India as global auto manufacturing hub",
            "Aftermarket premiumisation and tech-refresh trend",
            "Higher electronics content per vehicle (2x-3x growth)",
        ],
        "threats": [
            "Global Tier-1s entering Indian market aggressively",
            "Chinese component manufacturers (price competition)",
            "EV disruption making some traditional products obsolete",
            "OEMs backward-integrating into component manufacturing",
            "Regulatory changes and compliance costs",
        ],
    },
}

# Stock tickers for live data fetching
STOCK_TICKERS = {
    "UNO Minda": "UNOMINDA.NS",
    "Bosch Ltd": "BOSCHLTD.NS",
    "Motherson Intl": "MOTHERSON.NS",
    "Tube Investments": "TIINDIA.NS",
    "Endurance Tech": "ENDURANCE.NS",
    "Suprajit Eng": "SUPRAJIT.NS",
    "Gabriel India": "GABRIEL.NS",
    "Lumax Industries": "LUMAXIND.NS",
    "Motherson Sumi": "MSUMI.NS",
}

# Competitor news search topics
COMPETITOR_NEWS_TOPICS = {
    "Bosch India automotive": "Bosch Ltd (India)",
    "Samvardhana Motherson automotive": "Motherson International",
    "Endurance Technologies automotive": "Endurance Technologies",
    "Valeo automotive lighting": "Valeo (Global)",
    "Denso automotive components": "Denso (Global)",
    "Continental automotive ADAS": "Continental (Global)",
}
