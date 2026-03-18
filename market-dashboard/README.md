# Market Crisis Dashboard

A Streamlit web dashboard that aggregates free financial data sources to help navigate market crises.

## Features

- **Stock Heatmap** — S&P 500 treemap (size: market cap, color: daily change) via TradingView Screener
- **VIX Tracker** — Real-time CBOE Volatility Index with historical chart
- **Fear & Greed Index** — CNN's market sentiment gauge
- **Market Indices** — S&P 500, Dow, NASDAQ, Russell 2000, Gold, Oil, Bitcoin, etc.
- **Sector Performance** — All 11 GICS sectors with 1D/1W/1M performance
- **Market Breadth** — Advancing vs declining sector analysis
- **Financial News** — General market news and company-specific news via Finnhub

## Quick Start

```bash
cd market-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Optional: Finnhub API Key

For news headlines, get a free API key at [finnhub.io/register](https://finnhub.io/register):

```bash
export FINNHUB_API_KEY="your_key_here"
streamlit run app.py
```

Or enter it in the sidebar after launching the app.

## Data Sources

| Source | Data | Auth Required |
|--------|------|--------------|
| [yfinance](https://github.com/ranaroussi/yfinance) | Prices, VIX, sectors | No |
| [tradingview-screener](https://github.com/shner-elmo/TradingView-Screener) | Heatmap data | No |
| [Finnhub](https://finnhub.io/) | News, sentiment | Free API key |
| [CNN Fear & Greed](https://www.cnn.com/markets/fear-and-greed) | Sentiment index | No |
| [CBOE](https://www.cboe.com/) | Put/Call ratio | No |

## API Research

For full API research including endpoints, rate limits, and alternatives, see the plan file at the root of this project.
