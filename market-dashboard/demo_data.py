"""
Demo/sample data for testing the dashboard when external APIs are unavailable.
"""

import datetime

import pandas as pd


def demo_vix_data():
    dates = pd.date_range(end=datetime.date.today(), periods=120, freq="B")
    import random
    random.seed(42)
    values = [20.0]
    for _ in range(119):
        values.append(max(10, values[-1] + random.gauss(0, 1.5)))

    hist = pd.DataFrame({"Close": values}, index=dates)
    current = values[-1]
    prev = values[-2]
    change = ((current - prev) / prev) * 100

    level = "Normal"
    if current < 12:
        level = "Very Low — Complacency"
    elif current < 20:
        level = "Normal"
    elif current < 30:
        level = "Elevated — Caution"
    elif current < 40:
        level = "High — Fear"
    else:
        level = "Extreme — Panic"

    return {
        "current": round(current, 2),
        "change_pct": round(change, 2),
        "history": hist,
        "level": level,
    }


def demo_fear_greed():
    return {
        "score": 23.0,
        "rating": "Extreme Fear",
        "previous_close": 25.0,
        "one_week_ago": 30.0,
        "one_month_ago": 42.0,
        "one_year_ago": 65.0,
    }


def demo_market_indices():
    return [
        {"symbol": "^GSPC", "name": "S&P 500", "price": 5234.18, "change_pct": -1.42},
        {"symbol": "^DJI", "name": "Dow Jones", "price": 39142.23, "change_pct": -0.98},
        {"symbol": "^IXIC", "name": "NASDAQ", "price": 16274.94, "change_pct": -2.15},
        {"symbol": "^RUT", "name": "Russell 2000", "price": 2012.75, "change_pct": -1.87},
        {"symbol": "^VIX", "name": "VIX", "price": 28.34, "change_pct": 12.50},
        {"symbol": "^TNX", "name": "10Y Treasury Yield", "price": 4.32, "change_pct": -0.23},
        {"symbol": "GC=F", "name": "Gold", "price": 2978.40, "change_pct": 1.15},
        {"symbol": "CL=F", "name": "Crude Oil", "price": 67.82, "change_pct": -3.21},
        {"symbol": "BTC-USD", "name": "Bitcoin", "price": 82450.00, "change_pct": -4.30},
        {"symbol": "DX-Y.NYB", "name": "US Dollar Index", "price": 103.85, "change_pct": 0.45},
    ]


def demo_sector_performance():
    return pd.DataFrame([
        {"ETF": "XLK", "Sector": "Technology", "Price": 205.32, "1D %": -2.45, "1W %": -4.12, "1M %": -8.30},
        {"ETF": "XLF", "Sector": "Financials", "Price": 41.87, "1D %": -1.78, "1W %": -3.20, "1M %": -5.45},
        {"ETF": "XLV", "Sector": "Health Care", "Price": 138.95, "1D %": -0.65, "1W %": -1.80, "1M %": -2.10},
        {"ETF": "XLY", "Sector": "Consumer Disc.", "Price": 172.40, "1D %": -2.90, "1W %": -5.60, "1M %": -9.80},
        {"ETF": "XLP", "Sector": "Consumer Staples", "Price": 78.12, "1D %": 0.32, "1W %": 0.85, "1M %": 1.20},
        {"ETF": "XLE", "Sector": "Energy", "Price": 85.67, "1D %": -3.10, "1W %": -6.40, "1M %": -10.20},
        {"ETF": "XLI", "Sector": "Industrials", "Price": 118.43, "1D %": -1.55, "1W %": -2.90, "1M %": -4.75},
        {"ETF": "XLB", "Sector": "Materials", "Price": 82.90, "1D %": -1.20, "1W %": -2.40, "1M %": -3.50},
        {"ETF": "XLU", "Sector": "Utilities", "Price": 72.35, "1D %": 0.55, "1W %": 1.20, "1M %": 3.40},
        {"ETF": "XLRE", "Sector": "Real Estate", "Price": 38.90, "1D %": -0.85, "1W %": -1.50, "1M %": -2.80},
        {"ETF": "XLC", "Sector": "Comm. Services", "Price": 79.45, "1D %": -1.95, "1W %": -3.70, "1M %": -6.20},
    ])


def demo_heatmap():
    stocks = [
        ("AAPL", "Apple Inc", 172.50, -2.1, 2800e9, "Technology", "Consumer Electronics"),
        ("MSFT", "Microsoft Corp", 415.20, -1.8, 3100e9, "Technology", "Software"),
        ("GOOGL", "Alphabet Inc", 152.30, -2.5, 1900e9, "Communication Services", "Internet"),
        ("AMZN", "Amazon.com Inc", 178.90, -3.2, 1850e9, "Consumer Discretionary", "E-Commerce"),
        ("NVDA", "NVIDIA Corp", 875.40, -4.5, 2150e9, "Technology", "Semiconductors"),
        ("META", "Meta Platforms", 485.60, -2.8, 1250e9, "Communication Services", "Social Media"),
        ("BRK.B", "Berkshire Hathaway", 412.80, 0.3, 880e9, "Financials", "Insurance"),
        ("LLY", "Eli Lilly", 752.30, -1.2, 715e9, "Health Care", "Pharmaceuticals"),
        ("TSM", "Taiwan Semi", 142.60, -3.8, 740e9, "Technology", "Semiconductors"),
        ("V", "Visa Inc", 278.90, -0.9, 570e9, "Financials", "Payment Processing"),
        ("JPM", "JPMorgan Chase", 195.40, -1.5, 565e9, "Financials", "Banks"),
        ("UNH", "UnitedHealth", 485.20, -0.7, 450e9, "Health Care", "Health Insurance"),
        ("XOM", "Exxon Mobil", 105.30, -2.9, 420e9, "Energy", "Oil & Gas"),
        ("WMT", "Walmart Inc", 165.80, 0.4, 445e9, "Consumer Staples", "Retail"),
        ("MA", "Mastercard", 462.10, -1.0, 430e9, "Financials", "Payment Processing"),
        ("JNJ", "Johnson & Johnson", 158.70, -0.3, 382e9, "Health Care", "Pharmaceuticals"),
        ("PG", "Procter & Gamble", 162.40, 0.6, 380e9, "Consumer Staples", "Household Products"),
        ("HD", "Home Depot", 355.90, -2.2, 350e9, "Consumer Discretionary", "Home Improvement"),
        ("COST", "Costco", 725.30, -1.1, 322e9, "Consumer Staples", "Retail"),
        ("ABBV", "AbbVie Inc", 172.80, -0.8, 305e9, "Health Care", "Pharmaceuticals"),
        ("CVX", "Chevron Corp", 152.40, -2.6, 285e9, "Energy", "Oil & Gas"),
        ("BAC", "Bank of America", 35.20, -1.8, 280e9, "Financials", "Banks"),
        ("KO", "Coca-Cola", 62.30, 0.5, 268e9, "Consumer Staples", "Beverages"),
        ("PEP", "PepsiCo", 172.50, 0.2, 237e9, "Consumer Staples", "Beverages"),
        ("CSCO", "Cisco Systems", 48.90, -1.4, 199e9, "Technology", "Networking"),
    ]
    rows = []
    for name, desc, close, change, mcap, sector, industry in stocks:
        rows.append({
            "name": name, "description": desc, "close": close,
            "change": change, "market_cap_basic": mcap,
            "sector": sector, "industry": industry, "volume": 50_000_000,
        })
    return pd.DataFrame(rows)


def demo_market_breadth():
    return {
        "advancing_sectors": 3,
        "declining_sectors": 8,
        "ratio": 0.38,
        "signal": "Bearish",
    }


def demo_news():
    return [
        {"headline": "Markets tumble as tariff fears escalate", "source": "Reuters", "url": "#", "datetime": "2026-03-18 09:30", "summary": "Major indices fell sharply as new tariff announcements rattled investors.", "category": "general"},
        {"headline": "Fed signals potential rate adjustments amid volatility", "source": "CNBC", "url": "#", "datetime": "2026-03-18 08:15", "summary": "Federal Reserve officials indicated willingness to adjust monetary policy.", "category": "general"},
        {"headline": "Tech stocks lead market selloff for third straight day", "source": "Bloomberg", "url": "#", "datetime": "2026-03-18 07:45", "summary": "Technology sector continues to bear brunt of market decline.", "category": "general"},
        {"headline": "Gold reaches new highs as investors seek safe havens", "source": "MarketWatch", "url": "#", "datetime": "2026-03-18 07:00", "summary": "Gold prices surge as uncertainty drives safe-haven demand.", "category": "general"},
        {"headline": "VIX spikes above 28 signaling elevated market fear", "source": "Barron's", "url": "#", "datetime": "2026-03-17 16:30", "summary": "The fear index climbed sharply, reflecting growing investor anxiety.", "category": "general"},
        {"headline": "Treasury yields fall as bond market signals recession risk", "source": "WSJ", "url": "#", "datetime": "2026-03-17 15:00", "summary": "Bond markets pricing in higher probability of economic downturn.", "category": "general"},
        {"headline": "Energy sector hammered by oil price decline", "source": "Reuters", "url": "#", "datetime": "2026-03-17 14:30", "summary": "Crude oil drops below $68 amid demand concerns.", "category": "general"},
        {"headline": "Consumer confidence index falls to lowest level since 2022", "source": "AP", "url": "#", "datetime": "2026-03-17 10:00", "summary": "Consumer sentiment deteriorates amid economic uncertainty.", "category": "general"},
    ]
