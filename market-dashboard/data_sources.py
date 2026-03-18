"""
Data source modules for the market crisis dashboard.
Aggregates data from multiple free APIs.
"""

import datetime
import json
from typing import Optional

import pandas as pd
import requests
import yfinance as yf


# ---------------------------------------------------------------------------
# 1. TradingView Screener – SPX500 Heatmap Data
# ---------------------------------------------------------------------------

def get_tradingview_heatmap() -> pd.DataFrame:
    """Fetch SPX500 heatmap data using tradingview-screener."""
    try:
        from tradingview_screener import Query, col

        columns = [
            "name", "description", "close", "change", "change|1W", "change|1M",
            "volume", "market_cap_basic", "sector", "industry",
            "Perf.W", "Perf.1M", "Perf.3M", "Perf.YTD",
        ]

        _, df = (
            Query()
            .select(*columns)
            .where(col("is_primary") == True)
            .where(col("exchange").isin(["NYSE", "NASDAQ"]))
            .where(col("market_cap_basic") >= 10_000_000_000)
            .order_by("market_cap_basic", ascending=False)
            .limit(500)
            .get_scanner_data()
        )

        if "sector" in df.columns:
            df["sector"] = df["sector"].fillna("Unknown")
        return df

    except Exception as e:
        # Fallback: use yfinance for S&P 500 sector ETFs
        return _fallback_sector_data(str(e))


def _fallback_sector_data(error_msg: str) -> pd.DataFrame:
    """Fallback sector data via yfinance sector ETFs."""
    etfs = {
        "XLK": "Technology", "XLF": "Financials", "XLV": "Health Care",
        "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
        "XLE": "Energy", "XLI": "Industrials", "XLB": "Materials",
        "XLU": "Utilities", "XLRE": "Real Estate", "XLC": "Communication Services",
    }
    rows = []
    tickers = yf.Tickers(" ".join(etfs.keys()))
    for sym, sector in etfs.items():
        try:
            hist = tickers.tickers[sym].history(period="5d")
            if len(hist) >= 2:
                close = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = ((close - prev) / prev) * 100
                rows.append({
                    "name": sym, "description": sector, "close": close,
                    "change": change, "sector": sector,
                    "market_cap_basic": None, "volume": hist["Volume"].iloc[-1],
                    "_fallback": True, "_error": error_msg,
                })
        except Exception:
            continue
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. VIX & Volatility Data
# ---------------------------------------------------------------------------

def get_vix_data(period: str = "6mo") -> dict:
    """Fetch VIX current value and history via yfinance."""
    vix = yf.Ticker("^VIX")
    hist = vix.history(period=period)

    current = hist["Close"].iloc[-1] if len(hist) > 0 else None
    prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else None
    change = ((current - prev_close) / prev_close * 100) if (current and prev_close) else None

    return {
        "current": round(current, 2) if current else None,
        "change_pct": round(change, 2) if change else None,
        "history": hist,
        "level": _vix_level(current),
    }


def _vix_level(vix_val: Optional[float]) -> str:
    if vix_val is None:
        return "Unknown"
    if vix_val < 12:
        return "Very Low — Complacency"
    elif vix_val < 20:
        return "Normal"
    elif vix_val < 30:
        return "Elevated — Caution"
    elif vix_val < 40:
        return "High — Fear"
    else:
        return "Extreme — Panic"


# ---------------------------------------------------------------------------
# 3. CNN Fear & Greed Index
# ---------------------------------------------------------------------------

def get_fear_greed_index() -> dict:
    """Fetch CNN Fear & Greed Index."""
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            score = data.get("fear_and_greed", {}).get("score")
            rating = data.get("fear_and_greed", {}).get("rating")
            prev_close = data.get("fear_and_greed_historical", {}).get("previous_close")
            one_week = data.get("fear_and_greed_historical", {}).get("one_week_ago")
            one_month = data.get("fear_and_greed_historical", {}).get("one_month_ago")
            one_year = data.get("fear_and_greed_historical", {}).get("one_year_ago")
            return {
                "score": round(score, 1) if score else None,
                "rating": rating or _fg_rating(score),
                "previous_close": round(prev_close, 1) if prev_close else None,
                "one_week_ago": round(one_week, 1) if one_week else None,
                "one_month_ago": round(one_month, 1) if one_month else None,
                "one_year_ago": round(one_year, 1) if one_year else None,
            }
    except Exception:
        pass
    return {"score": None, "rating": "Unavailable", "error": "Could not fetch CNN Fear & Greed"}


def _fg_rating(score: Optional[float]) -> str:
    if score is None:
        return "Unknown"
    if score <= 25:
        return "Extreme Fear"
    elif score <= 45:
        return "Fear"
    elif score <= 55:
        return "Neutral"
    elif score <= 75:
        return "Greed"
    else:
        return "Extreme Greed"


# ---------------------------------------------------------------------------
# 4. Market Indices & Sector Performance
# ---------------------------------------------------------------------------

def get_market_indices() -> list[dict]:
    """Fetch key market indices."""
    symbols = {
        "^GSPC": "S&P 500", "^DJI": "Dow Jones", "^IXIC": "NASDAQ",
        "^RUT": "Russell 2000", "^VIX": "VIX",
        "^TNX": "10Y Treasury Yield", "GC=F": "Gold", "CL=F": "Crude Oil",
        "BTC-USD": "Bitcoin", "DX-Y.NYB": "US Dollar Index",
    }
    results = []
    tickers = yf.Tickers(" ".join(symbols.keys()))
    for sym, name in symbols.items():
        try:
            t = tickers.tickers[sym]
            hist = t.history(period="5d")
            if len(hist) >= 2:
                close = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = ((close - prev) / prev) * 100
                results.append({
                    "symbol": sym, "name": name,
                    "price": round(close, 2), "change_pct": round(change, 2),
                })
        except Exception:
            continue
    return results


def get_sector_performance() -> pd.DataFrame:
    """Get sector ETF performance across multiple timeframes."""
    etfs = {
        "XLK": "Technology", "XLF": "Financials", "XLV": "Health Care",
        "XLY": "Consumer Disc.", "XLP": "Consumer Staples",
        "XLE": "Energy", "XLI": "Industrials", "XLB": "Materials",
        "XLU": "Utilities", "XLRE": "Real Estate", "XLC": "Comm. Services",
    }
    rows = []
    for sym, name in etfs.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="3mo")
            if len(hist) < 2:
                continue
            close = hist["Close"].iloc[-1]
            day_chg = ((close - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]) * 100

            week_chg = month_chg = None
            if len(hist) >= 5:
                week_chg = ((close - hist["Close"].iloc[-5]) / hist["Close"].iloc[-5]) * 100
            if len(hist) >= 22:
                month_chg = ((close - hist["Close"].iloc[-22]) / hist["Close"].iloc[-22]) * 100

            rows.append({
                "ETF": sym, "Sector": name, "Price": round(close, 2),
                "1D %": round(day_chg, 2),
                "1W %": round(week_chg, 2) if week_chg else None,
                "1M %": round(month_chg, 2) if month_chg else None,
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Financial News (Finnhub — free tier, 50 req/min)
# ---------------------------------------------------------------------------

def get_market_news(finnhub_api_key: Optional[str] = None) -> list[dict]:
    """Fetch general market news from Finnhub."""
    if not finnhub_api_key:
        return [{"headline": "Set FINNHUB_API_KEY for news", "source": "", "url": "https://finnhub.io/register"}]

    try:
        import finnhub
        client = finnhub.Client(api_key=finnhub_api_key)
        news = client.general_news("general", min_id=0)
        results = []
        for item in news[:20]:
            results.append({
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary", ""),
                "datetime": datetime.datetime.fromtimestamp(
                    item.get("datetime", 0)
                ).strftime("%Y-%m-%d %H:%M") if item.get("datetime") else "",
                "category": item.get("category", ""),
            })
        return results
    except Exception as e:
        return [{"headline": f"Error fetching news: {e}", "source": "", "url": ""}]


def get_company_news(symbol: str, finnhub_api_key: Optional[str] = None) -> list[dict]:
    """Fetch company-specific news from Finnhub."""
    if not finnhub_api_key:
        return []
    try:
        import finnhub
        client = finnhub.Client(api_key=finnhub_api_key)
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        news = client.company_news(symbol, _from=str(week_ago), to=str(today))
        return [
            {
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "datetime": datetime.datetime.fromtimestamp(
                    item.get("datetime", 0)
                ).strftime("%Y-%m-%d %H:%M") if item.get("datetime") else "",
            }
            for item in news[:10]
        ]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# 6. Market Breadth (via yfinance — advancing vs declining)
# ---------------------------------------------------------------------------

def get_market_breadth() -> dict:
    """Estimate market breadth using S&P 500 sector ETFs and key indicators."""
    try:
        # Use advance/decline data from key ETFs as a proxy
        spy = yf.Ticker("SPY")
        hist = spy.history(period="5d")
        if len(hist) < 2:
            return {"status": "Unavailable"}

        # McClellan-style: check how many sector ETFs are up vs down
        etfs = ["XLK", "XLF", "XLV", "XLY", "XLP", "XLE", "XLI", "XLB", "XLU", "XLRE", "XLC"]
        advancing = 0
        declining = 0
        for sym in etfs:
            try:
                t = yf.Ticker(sym)
                h = t.history(period="2d")
                if len(h) >= 2:
                    if h["Close"].iloc[-1] > h["Close"].iloc[-2]:
                        advancing += 1
                    else:
                        declining += 1
            except Exception:
                continue

        ratio = advancing / max(declining, 1)
        return {
            "advancing_sectors": advancing,
            "declining_sectors": declining,
            "ratio": round(ratio, 2),
            "signal": "Bullish" if ratio > 1.5 else ("Bearish" if ratio < 0.67 else "Neutral"),
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


# ---------------------------------------------------------------------------
# 7. Put/Call Ratio (CBOE)
# ---------------------------------------------------------------------------

def get_put_call_ratio() -> dict:
    """Attempt to get put/call ratio data."""
    try:
        # CBOE publishes daily data — try to scrape the latest
        url = "https://www.cboe.com/us/options/market_statistics/daily/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        # This often blocks automated access; provide manual link
        return {
            "source": "CBOE",
            "url": "https://www.cboe.com/us/options/market_statistics/daily/",
            "note": "Visit CBOE directly for latest put/call ratio data",
        }
    except Exception:
        return {"source": "CBOE", "url": "https://www.cboe.com/us/options/market_statistics/daily/"}
