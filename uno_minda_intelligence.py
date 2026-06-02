#!/usr/bin/env python3
"""
=============================================================================
  UNO MINDA - Comprehensive Business Intelligence & Competitor News Tracker
=============================================================================
  This script, when invoked, fetches and displays:
    1. UNO Minda company overview & business segments
    2. Product portfolio details
    3. Indian & Global competitors
    4. Current partnerships, JVs, and agreements
    5. Market analysis (financials, growth, positioning)
    6. Latest news about UNO Minda
    7. Latest news about each competitor
    8. EV strategy and future outlook

  Requirements: pip install requests beautifulsoup4 yfinance pandas rich colorama

  Usage:
    python uno_minda_intelligence.py              # Full report
    python uno_minda_intelligence.py --news       # News only
    python uno_minda_intelligence.py --competitors # Competitor news only
    python uno_minda_intelligence.py --stock      # Stock & financial data only
    python uno_minda_intelligence.py --export     # Export full report to JSON
=============================================================================
"""

import json
import sys
import os
import datetime
import argparse
import textwrap
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    import yfinance as yf
    import pandas as pd
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
except ImportError as e:
    print(f"Missing package: {e}")
    print("Install with: pip install requests beautifulsoup4 yfinance pandas rich colorama")
    sys.exit(1)

console = Console()

# ==============================================================================
# STATIC DATA: UNO Minda Company Profile
# ==============================================================================

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
    "Joint Ventures (13 total)": {
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
    "Strategic Partnerships & Agreements": {
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
    "Recent Strategic Moves": {
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


# ==============================================================================
# WEB SEARCH FUNCTION (using requests to a search API or scraping)
# ==============================================================================

def search_web(query, num_results=10):
    """
    Search the web using DuckDuckGo HTML version (no API key needed).
    Returns list of search result dicts.
    """
    results = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for r in soup.find_all("div", class_="result", limit=num_results):
            title_tag = r.find("a", class_="result__a")
            snippet_tag = r.find("a", class_="result__snippet")
            if title_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": title_tag.get("href", ""),
                    "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                })
    except Exception as e:
        results.append({"error": f"Search failed: {str(e)}"})
    return results


def resolve_google_news_url(url, timeout=10):
    """
    Resolve a Google News redirect URL to the actual article URL.
    Google News RSS feeds use encoded redirect URLs that need to be followed
    to get the real article URL.
    """
    if not url or not url.startswith("http"):
        return url

    # If it's a Google News redirect URL, try to follow it
    if "news.google.com" in url or "news.google.co" in url:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            }
            resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            # The final URL after redirects is the actual article URL
            final_url = resp.url
            # If still on Google News, try to extract the article content from the Google News page itself
            if "news.google.com" in final_url:
                # Try to extract the actual article from the Google News page
                soup = BeautifulSoup(resp.text, "html.parser")
                # Look for canonical link or the actual article link
                canonical = soup.find("link", rel="canonical")
                if canonical and canonical.get("href"):
                    return canonical["href"]
                # Look for the amp-url or og:url
                og_url = soup.find("meta", property="og:url")
                if og_url and og_url.get("content"):
                    return og_url["content"]
                # If all else fails, try to extract the article text from the Google News page itself
                return final_url
            return final_url
        except Exception:
            return url

    return url


def search_news_direct(topic, num=10):
    """
    Search for news using DuckDuckGo which gives direct article URLs.
    Returns list of news article dicts with direct URLs.
    """
    results = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        query = f"{topic} latest news"
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for r in soup.find_all("div", class_="result", limit=num):
            title_tag = r.find("a", class_="result__a")
            snippet_tag = r.find("a", class_="result__snippet")
            if title_tag:
                ddg_url = title_tag.get("href", "")
                # Extract actual URL from DuckDuckGo redirect
                actual_url = ddg_url
                if "uddg=" in ddg_url:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(ddg_url)
                    params = urllib.parse.parse_qs(parsed.query)
                    if "uddg" in params:
                        actual_url = urllib.parse.unquote(params["uddg"][0])

                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": actual_url,
                    "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                    "source": "",
                    "date": "",
                })
    except Exception as e:
        results.append({"error": f"News search failed: {str(e)}"})
    return results


def fetch_full_article(url, timeout=12):
    """
    Fetch the full article content from a given URL.
    Uses multiple extraction strategies to handle different website layouts.
    Returns the full article text, or a descriptive error message.
    """
    if not url or not url.startswith("http"):
        return "[Full article unavailable - invalid URL]"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()

        # Stop if we get a non-HTML content type
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" in content_type or "image" in content_type or "video" in content_type:
            return "[Full article is a PDF/media file - cannot extract text]"

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove unwanted elements
        for tag in soup.find_all(["script", "style", "nav", "footer", "header",
                                  "aside", "iframe", "noscript", "form",
                                  "button", "input", "select", "textarea"]):
            tag.decompose()

        # Strategy 1: Look for <article> tag (most modern news sites)
        article_tag = soup.find("article")
        if article_tag:
            text = article_tag.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return _clean_article_text(text)

        # Strategy 2: Look for common content class/id patterns
        content_patterns = [
            {"class_": lambda x: x and any(k in " ".join(x) for k in
             ["article-content", "article-body", "article__body", "article_text",
              "story-content", "story-body", "story_content", "post-content",
              "entry-content", "content-body", "main-content", "detail-content",
              "news-content", "article-detail", "artcile-body", "ArticleBody",
              "articleBody", "post-body", "entry-body"])},
            {"id": lambda x: x and any(k in str(x) for k in
             ["article-content", "article-body", "story-content", "post-content",
              "entry-content", "main-content", "article_content", "content-body",
              "ArticleBody", "articleBody"])},
        ]
        for pattern in content_patterns:
            content_div = soup.find("div", **pattern)
            if content_div:
                text = content_div.get_text(separator="\n", strip=True)
                if len(text) > 200:
                    return _clean_article_text(text)

        # Strategy 3: Look for multiple <p> tags inside the main content area
        # Find the container with the most <p> tags (likely the article body)
        all_divs = soup.find_all("div")
        best_div = None
        max_p_count = 0
        for div in all_divs:
            p_count = len(div.find_all("p", recursive=False))
            if p_count > max_p_count:
                max_p_count = p_count
                best_div = div
        if best_div and max_p_count >= 3:
            paragraphs = best_div.find_all("p")
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            if len(text) > 200:
                return _clean_article_text(text)

        # Strategy 4: Just get all <p> tags from the page
        all_p = soup.find_all("p")
        if all_p:
            text = "\n\n".join(p.get_text(strip=True) for p in all_p if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30)
            if len(text) > 200:
                return _clean_article_text(text)

        return "[Full article text could not be extracted from this page]"

    except requests.exceptions.Timeout:
        return "[Full article unavailable - request timed out]"
    except requests.exceptions.ConnectionError:
        return "[Full article unavailable - connection error]"
    except requests.exceptions.HTTPError as e:
        return f"[Full article unavailable - HTTP error: {e.response.status_code}]"
    except Exception as e:
        return f"[Full article unavailable - error: {str(e)[:100]}]"


def _clean_article_text(text):
    """
    Clean and format the extracted article text.
    Remove excessive whitespace, limit length, and format nicely.
    """
    # Remove excessive blank lines
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    cleaned = "\n\n".join(cleaned_lines)

    # Cap at 5000 characters for display, add ellipsis if truncated
    if len(cleaned) > 5000:
        cleaned = cleaned[:5000] + "\n\n... [Article truncated - full article is longer]"

    return cleaned


def fetch_news_from_google(topic, num=10, fetch_articles=True):
    """
    Fetch news articles for a topic using DuckDuckGo search (gives direct URLs).
    Also fetches the full article content from each news URL.
    """
    results = []
    try:
        # Use DuckDuckGo for direct URLs (Google News RSS has redirect URLs)
        search_results = search_news_direct(topic, num)
        for item in search_results:
            if "error" in item:
                results.append(item)
                continue

            article_url = item.get("url", "")

            article_data = {
                "title": item.get("title", ""),
                "url": article_url,
                "date": item.get("date", ""),
                "snippet": item.get("snippet", "")[:300],
                "source": item.get("source", ""),
                "full_article": "",
            }

            # Fetch the full article content
            if fetch_articles and article_url:
                console.print(f"     [dim]Fetching full article: {article_data['title'][:60]}...[/dim]")
                article_data["full_article"] = fetch_full_article(article_url)

            results.append(article_data)
    except Exception as e:
        results.append({"error": f"News fetch failed: {str(e)}"})
    return results


def fetch_stock_data(ticker_symbol):
    """
    Fetch stock data using yfinance.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        hist = stock.history(period="1mo")

        current_price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        prev_close = info.get("previousClose", "N/A")
        market_cap = info.get("marketCap", "N/A")
        pe_ratio = info.get("trailingPE", "N/A")
        revenue = info.get("totalRevenue", "N/A")
        profit_margin = info.get("profitMargins", "N/A")

        if market_cap and market_cap != "N/A" and isinstance(market_cap, (int, float)):
            market_cap = f"INR {market_cap / 1e7:.0f} Crore" if market_cap > 1e12 else f"INR {market_cap / 1e7:.1f} Crore"
        if revenue and revenue != "N/A" and isinstance(revenue, (int, float)):
            revenue = f"INR {revenue / 1e7:.0f} Crore"

        return {
            "ticker": ticker_symbol,
            "current_price": current_price,
            "prev_close": prev_close,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "revenue_ttm": revenue,
            "profit_margin": f"{profit_margin * 100:.1f}%" if isinstance(profit_margin, float) else "N/A",
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
    except Exception as e:
        return {"ticker": ticker_symbol, "error": str(e)}


# ==============================================================================
# DISPLAY FUNCTIONS
# ==============================================================================

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║       UNO MINDA - Business Intelligence & News Tracker          ║
    ║       Comprehensive Competitor & Market Analysis Tool           ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"    Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
    console.print()


def display_company_overview():
    console.print(Panel("[bold green]COMPANY OVERVIEW - UNO MINDA LIMITED[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Field", style="bold yellow", width=28)
    table.add_column("Details", style="white", width=80)

    for key, value in UNO_MINDA_PROFILE.items():
        formatted_key = key.replace("_", " ").title()
        table.add_row(formatted_key, str(value))

    console.print(table)
    console.print()


def display_product_portfolio():
    console.print(Panel("[bold green]PRODUCT PORTFOLIO - 26+ PRODUCT LINES[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    for category, details in PRODUCT_PORTFOLIO.items():
        console.print(f"\n[bold cyan]{category}[/bold cyan] [dim]({details['market_position']})[/dim]")
        console.print(f"  Segments: {', '.join(details['segments'])}")
        console.print(f"  Products: {', '.join(details['products'][:6])}")
        if len(details['products']) > 6:
            console.print(f"           {', '.join(details['products'][6:])}")
    console.print()


def display_competitors():
    console.print(Panel("[bold green]COMPETITIVE LANDSCAPE[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    # Indian competitors
    console.print("\n[bold yellow]INDIAN MARKET COMPETITORS[/bold yellow]\n")
    for name, details in COMPETITORS["indian"].items():
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1), title=name)
        table.add_column("Field", style="bold", width=22)
        table.add_column("Details", style="white", width=80)
        table.add_row("Headquarters", details["headquarters"])
        table.add_row("Revenue (Approx)", details["revenue_approx"])
        table.add_row("Key Products", ", ".join(details["key_products"][:5]))
        table.add_row("Competition Areas", ", ".join(details["competition_areas"]))
        table.add_row("Market Position", details["market_position"])
        table.add_row("Strength", details["strength"])
        if details.get("ticker"):
            table.add_row("Stock Ticker", details["ticker"])
        console.print(table)
        console.print()

    # Global competitors
    console.print("[bold yellow]GLOBAL MARKET COMPETITORS[/bold yellow]\n")
    for name, details in COMPETITORS["global"].items():
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1), title=name)
        table.add_column("Field", style="bold", width=22)
        table.add_column("Details", style="white", width=80)
        table.add_row("Headquarters", details["headquarters"])
        table.add_row("Revenue (Approx)", details["revenue_approx"])
        table.add_row("Key Products", ", ".join(details["key_products"][:5]))
        table.add_row("Competition Areas", ", ".join(details["competition_areas"]))
        table.add_row("Market Position", details["market_position"])
        table.add_row("Strength", details["strength"])
        if details.get("ticker"):
            table.add_row("Stock Ticker", details["ticker"])
        console.print(table)
        console.print()


def display_partnerships():
    console.print(Panel("[bold green]PARTNERSHIPS, JOINT VENTURES & AGREEMENTS[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    # JVs
    console.print("\n[bold yellow]JOINT VENTURES (13 Total; 10 Japanese, 2 European, 1 Canadian)[/bold yellow]\n")
    for name, details in PARTNERSHIPS_AND_JVS["Joint Ventures (13 total)"].items():
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1), title=name)
        table.add_column("Field", style="bold", width=22)
        table.add_column("Details", style="white", width=80)
        table.add_row("Entity", details["entity"])
        table.add_row("Equity", details["equity"])
        table.add_row("Products", details["products"])
        table.add_row("Status", details["status"])
        table.add_row("Notes", details["notes"])
        console.print(table)
        console.print()

    # Strategic Partnerships
    console.print("[bold yellow]STRATEGIC PARTNERSHIPS[/bold yellow]\n")
    for name, details in PARTNERSHIPS_AND_JVS["Strategic Partnerships & Agreements"].items():
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1), title=name)
        table.add_column("Field", style="bold", width=22)
        table.add_column("Details", style="white", width=80)
        for k, v in details.items():
            table.add_row(k.replace("_", " ").title(), str(v))
        console.print(table)
        console.print()

    # Recent Strategic Moves
    console.print("[bold yellow]RECENT STRATEGIC MOVES[/bold yellow]\n")
    for key, value in PARTNERSHIPS_AND_JVS["Recent Strategic Moves"].items():
        console.print(f"  [cyan]{key.replace('_', ' ').title()}:[/cyan] {value}")
    console.print()


def display_market_analysis():
    console.print(Panel("[bold green]MARKET ANALYSIS[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    # Industry Overview
    console.print("\n[bold yellow]INDUSTRY OVERVIEW[/bold yellow]\n")
    for key, value in MARKET_ANALYSIS["industry_overview"].items():
        if isinstance(value, list):
            console.print(f"  [cyan]{key.replace('_', ' ').title()}:[/cyan]")
            for item in value:
                console.print(f"    - {item}")
        else:
            console.print(f"  [cyan]{key.replace('_', ' ').title()}:[/cyan] {value}")

    # Market Position
    console.print("\n[bold yellow]UNO MINDA MARKET POSITION[/bold yellow]\n")
    for key, value in MARKET_ANALYSIS["uno_minda_market_position"].items():
        if isinstance(value, list):
            console.print(f"  [cyan]{key.replace('_', ' ').title()}:[/cyan]")
            for item in value:
                console.print(f"    - {item}")
        else:
            console.print(f"  [cyan]{key.replace('_', ' ').title()}:[/cyan] {value}")

    # Financial Summary
    console.print("\n[bold yellow]FINANCIAL SUMMARY[/bold yellow]\n")
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Metric", style="bold yellow", width=30)
    table.add_column("Value", style="white", width=50)
    for key, value in MARKET_ANALYSIS["financial_summary"].items():
        table.add_row(key.replace("_", " ").title(), str(value))
    console.print(table)

    # SWOT
    console.print("\n[bold yellow]SWOT ANALYSIS[/bold yellow]\n")
    for category, items in MARKET_ANALYSIS["swot"].items():
        color = {"strengths": "green", "weaknesses": "red", "opportunities": "blue", "threats": "magenta"}[category]
        console.print(f"  [{color}]{category.upper()}[/{color}]")
        for item in items:
            console.print(f"    - {item}")
        console.print()


def _display_single_article(article, index):
    """Helper to display a single news article with full content."""
    if "error" in article:
        console.print(f"  [red]Error: {article['error']}[/red]")
        return

    title = article.get("title", "No Title")
    date = article.get("date", "")
    source = article.get("source", "")
    url = article.get("url", "")
    snippet = article.get("snippet", "")
    full_article = article.get("full_article", "")

    # Header with title and metadata
    console.print(f"  [bold cyan]{index}. {title}[/bold cyan]")
    meta_parts = []
    if source:
        meta_parts.append(f"Source: {source}")
    if date:
        meta_parts.append(f"Date: {date}")
    if meta_parts:
        console.print(f"     [dim]{' | '.join(meta_parts)}[/dim]")
    if url:
        console.print(f"     [dim blue]{url}[/dim blue]")

    # Display full article content if available
    if full_article and not full_article.startswith("["):
        console.print()
        console.print(Panel(
            full_article,
            title="[bold]FULL ARTICLE[/bold]",
            border_style="dim green",
            padding=(1, 2),
            expand=False,
        ))
    elif full_article:
        # Full article extraction failed - show the snippet instead
        console.print(f"     [yellow]{full_article}[/yellow]")
        if snippet:
            console.print(f"     [dim]Snippet: {snippet[:250]}[/dim]")
    elif snippet:
        # No full article fetched - show snippet
        console.print(f"     [dim]{snippet[:250]}[/dim]")

    console.print()


def display_news_section():
    console.print(Panel("[bold green]LATEST NEWS - UNO MINDA & COMPETITORS (with Full Articles)[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    # UNO Minda News
    console.print("\n[bold yellow]UNO MINDA NEWS (Live from Web)[/bold yellow]\n")
    news = fetch_news_from_google("UNO Minda automotive", 10, fetch_articles=True)
    if news:
        for i, article in enumerate(news, 1):
            _display_single_article(article, i)
    else:
        console.print("  [dim]No news found.[/dim]")

    # Competitor News
    competitor_news_topics = {
        "Bosch India automotive": "Bosch Ltd (India)",
        "Samvardhana Motherson automotive": "Motherson International",
        "Endurance Technologies automotive": "Endurance Technologies",
        "Valeo automotive lighting": "Valeo (Global)",
        "Denso automotive components": "Denso (Global)",
        "Continental automotive ADAS": "Continental (Global)",
    }

    for topic, company_name in competitor_news_topics.items():
        console.print(f"\n[bold yellow]NEWS: {company_name}[/bold yellow]\n")
        comp_news = fetch_news_from_google(topic, 5, fetch_articles=True)
        if comp_news:
            for i, article in enumerate(comp_news, 1):
                _display_single_article(article, i)
        else:
            console.print("  [dim]No news found.[/dim]")


def display_stock_data():
    console.print(Panel("[bold green]STOCK & FINANCIAL DATA (Live)[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    tickers = {
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

    table = Table(show_header=True, box=box.ROUNDED, title="Competitor Stock Comparison")
    table.add_column("Company", style="bold cyan", width=18)
    table.add_column("Current Price", style="green", width=14)
    table.add_column("Market Cap", style="yellow", width=22)
    table.add_column("P/E Ratio", style="white", width=10)
    table.add_column("Revenue (TTM)", style="white", width=18)
    table.add_column("Profit Margin", style="white", width=14)
    table.add_column("52W High", style="white", width=14)
    table.add_column("52W Low", style="white", width=14)

    for company, ticker in tickers.items():
        console.print(f"  Fetching {company}...", style="dim")
        data = fetch_stock_data(ticker)
        if "error" in data:
            table.add_row(company, "Error", "", "", "", "", "", "")
        else:
            table.add_row(
                company,
                str(data.get("current_price", "N/A")),
                str(data.get("market_cap", "N/A")),
                str(data.get("pe_ratio", "N/A")),
                str(data.get("revenue_ttm", "N/A")),
                str(data.get("profit_margin", "N/A")),
                str(data.get("52w_high", "N/A")),
                str(data.get("52w_low", "N/A")),
            )

    console.print(table)
    console.print()


def display_web_search_results():
    """Perform additional web searches for the latest UNO Minda information, with full article content."""
    console.print(Panel("[bold green]WEB SEARCH RESULTS (Live - with Full Articles)[/bold green]",
                        box=box.DOUBLE, border_style="green"))

    search_queries = [
        "UNO Minda latest news 2026",
        "UNO Minda EV strategy India",
        "UNO Minda competitors market share India",
    ]

    for query in search_queries:
        console.print(f"\n[bold yellow]Search: {query}[/bold yellow]\n")
        results = search_web(query, 5)
        for i, result in enumerate(results, 1):
            if "error" in result:
                console.print(f"  [red]Error: {result['error']}[/red]")
                continue

            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("snippet", "")

            console.print(f"  [bold cyan]{i}. {title}[/bold cyan]")
            if url:
                console.print(f"     [dim blue]{url}[/dim blue]")

            # Fetch and display full article content
            if url and url.startswith("http"):
                console.print(f"     [dim]Fetching full article...[/dim]")
                full_text = fetch_full_article(url)
                if full_text and not full_text.startswith("["):
                    console.print(Panel(
                        full_text,
                        title="[bold]FULL ARTICLE[/bold]",
                        border_style="dim green",
                        padding=(1, 2),
                        expand=False,
                    ))
                elif full_text:
                    console.print(f"     [yellow]{full_text}[/yellow]")
                    if snippet:
                        console.print(f"     [dim]Snippet: {snippet[:250]}[/dim]")
                elif snippet:
                    console.print(f"     [dim]{snippet[:250]}[/dim]")
            elif snippet:
                console.print(f"     [dim]{snippet[:250]}[/dim]")

            console.print()


def export_to_json():
    """Export all data to a JSON file, including full article content."""
    console.print("[bold yellow]Exporting full report with article content to JSON...[/bold yellow]")
    console.print("[dim]This may take a while as full articles are fetched from each URL.[/dim]\n")

    export_data = {
        "report_date": datetime.datetime.now().isoformat(),
        "company_profile": UNO_MINDA_PROFILE,
        "product_portfolio": PRODUCT_PORTFOLIO,
        "competitors": COMPETITORS,
        "partnerships_and_jvs": PARTNERSHIPS_AND_JVS,
        "market_analysis": MARKET_ANALYSIS,
        "live_news": {
            "uno_minda": fetch_news_from_google("UNO Minda automotive", 10, fetch_articles=True),
            "competitor_news": {},
        },
        "live_stock_data": {},
    }

    # Competitor news with full articles
    competitor_topics = {
        "Bosch India automotive": "Bosch",
        "Samvardhana Motherson automotive": "Motherson",
        "Endurance Technologies automotive": "Endurance",
        "Valeo automotive": "Valeo",
        "Denso automotive": "Denso",
        "Continental automotive ADAS": "Continental",
    }
    for topic, name in competitor_topics.items():
        export_data["live_news"]["competitor_news"][name] = fetch_news_from_google(topic, 5, fetch_articles=True)

    # Stock data
    tickers = {
        "UNO Minda": "UNOMINDA.NS",
        "Bosch Ltd": "BOSCHLTD.NS",
        "Motherson Intl": "MOTHERSON.NS",
        "Endurance Tech": "ENDURANCE.NS",
        "Suprajit Eng": "SUPRAJIT.NS",
    }
    for company, ticker in tickers.items():
        export_data["live_stock_data"][company] = fetch_stock_data(ticker)

    filepath = f"/home/z/my-project/download/uno_minda_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    console.print(f"\n[bold green]Report exported to: {filepath}[/bold green]")
    return filepath


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="UNO Minda - Business Intelligence & Competitor News Tracker"
    )
    parser.add_argument("--news", action="store_true", help="Show news only (UNO Minda + competitors)")
    parser.add_argument("--competitors", action="store_true", help="Show competitor analysis + news only")
    parser.add_argument("--stock", action="store_true", help="Show stock & financial data only")
    parser.add_argument("--export", action="store_true", help="Export full report to JSON file")
    parser.add_argument("--full", action="store_true", help="Full comprehensive report (default)")
    args = parser.parse_args()

    # If no specific flag, show full report
    show_full = not any([args.news, args.competitors, args.stock, args.export])

    if show_full or args.full:
        print_banner()
        display_company_overview()
        display_product_portfolio()
        display_competitors()
        display_partnerships()
        display_market_analysis()
        display_stock_data()
        display_news_section()
        display_web_search_results()

    elif args.news:
        print_banner()
        display_news_section()
        display_web_search_results()

    elif args.competitors:
        print_banner()
        display_competitors()
        display_news_section()

    elif args.stock:
        print_banner()
        display_stock_data()

    if args.export:
        print_banner()
        export_to_json()

    console.print("\n[bold green]Report Complete.[/bold green]")
    console.print("[dim]Data sources: Company filings, Google News, Yahoo Finance, DuckDuckGo Search[/dim]")
    console.print("[dim]Note: Live data may vary based on API availability and market hours.[/dim]")


if __name__ == "__main__":
    main()
