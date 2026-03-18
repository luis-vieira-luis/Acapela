"""
Market Crisis Dashboard — Streamlit Web App
Aggregates free financial data for navigating market crises.

Usage:
    pip install -r requirements.txt
    streamlit run app.py

Optional: Set FINNHUB_API_KEY env var for news (free at https://finnhub.io/register)
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_sources import (
    get_company_news,
    get_fear_greed_index,
    get_market_breadth,
    get_market_indices,
    get_market_news,
    get_put_call_ratio,
    get_sector_performance,
    get_tradingview_heatmap,
    get_vix_data,
)
from demo_data import (
    demo_fear_greed,
    demo_heatmap,
    demo_market_breadth,
    demo_market_indices,
    demo_news,
    demo_sector_performance,
    demo_vix_data,
)


def safe_call(live_fn, demo_fn, *args, **kwargs):
    """Try the live data source; fall back to demo data on failure."""
    try:
        result = live_fn(*args, **kwargs)
        # Check if result is usable
        if result is None:
            return demo_fn(), True
        if isinstance(result, pd.DataFrame) and result.empty:
            return demo_fn(), True
        if isinstance(result, dict) and result.get("current") is None and "history" in result:
            return demo_fn(), True
        if isinstance(result, list) and len(result) == 0:
            return demo_fn(), True
        return result, False
    except Exception:
        return demo_fn(), True

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Market Crisis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Market Crisis Dashboard")
st.caption("Real-time aggregation of free financial data sources")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
using_demo = False

with st.sidebar:
    st.header("Settings")
    finnhub_key = st.text_input(
        "Finnhub API Key (optional)",
        value=os.environ.get("FINNHUB_API_KEY", ""),
        type="password",
        help="Get a free key at https://finnhub.io/register",
    )
    st.divider()
    st.markdown("""
    **Data Sources:**
    - [yfinance](https://github.com/ranaroussi/yfinance) — Prices, VIX
    - [tradingview-screener](https://github.com/shner-elmo/TradingView-Screener) — Heatmap
    - [Finnhub](https://finnhub.io/) — News & sentiment
    - [CNN Fear & Greed](https://www.cnn.com/markets/fear-and-greed) — Sentiment
    - [CBOE](https://www.cboe.com/) — Put/Call ratio
    """)
    if st.button("Refresh All Data"):
        st.cache_data.clear()
        st.rerun()


# ---------------------------------------------------------------------------
# Row 1: Key Indicators
# ---------------------------------------------------------------------------
st.header("Key Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.spinner("Loading VIX..."):
        vix, vix_demo = safe_call(get_vix_data, demo_vix_data)
        using_demo = using_demo or vix_demo
    st.metric(
        "VIX (Fear Index)",
        vix["current"],
        delta=f"{vix['change_pct']}%" if vix["change_pct"] else None,
        delta_color="inverse",
    )
    st.caption(vix["level"])

with col2:
    with st.spinner("Loading Fear & Greed..."):
        fg, fg_demo = safe_call(get_fear_greed_index, demo_fear_greed)
        using_demo = using_demo or fg_demo
    score = fg.get("score")
    rating = fg.get("rating", "N/A")
    st.metric("Fear & Greed Index", score if score else "N/A")
    if score is not None:
        color = "red" if score <= 25 else ("orange" if score <= 45 else ("gray" if score <= 55 else ("lightgreen" if score <= 75 else "green")))
        st.markdown(f":{color}[**{rating}**]")
    else:
        st.caption(rating)

with col3:
    with st.spinner("Loading breadth..."):
        breadth, breadth_demo = safe_call(get_market_breadth, demo_market_breadth)
        using_demo = using_demo or breadth_demo
    if "advancing_sectors" in breadth:
        st.metric(
            "Market Breadth",
            f"{breadth['advancing_sectors']}A / {breadth['declining_sectors']}D",
        )
        st.caption(f"Signal: {breadth['signal']} (ratio {breadth['ratio']})")
    else:
        st.metric("Market Breadth", "N/A")

with col4:
    pc = get_put_call_ratio()
    st.metric("Put/Call Ratio", "See CBOE")
    st.caption(f"[View on CBOE]({pc['url']})")

if using_demo:
    st.info("Using demo data — external APIs are unreachable. Run locally for live data.")


# ---------------------------------------------------------------------------
# Row 2: Market Indices
# ---------------------------------------------------------------------------
st.header("Market Indices")
with st.spinner("Loading indices..."):
    indices, _ = safe_call(get_market_indices, demo_market_indices)

if indices:
    cols = st.columns(min(len(indices), 5))
    for i, idx in enumerate(indices):
        with cols[i % 5]:
            delta_color = "normal"
            if idx["name"] == "VIX":
                delta_color = "inverse"
            st.metric(
                idx["name"],
                f"{idx['price']:,.2f}",
                delta=f"{idx['change_pct']:+.2f}%",
                delta_color=delta_color,
            )


# ---------------------------------------------------------------------------
# Row 3: VIX History Chart
# ---------------------------------------------------------------------------
st.header("VIX History")
vix_period = st.selectbox("VIX Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
vix_data, _ = safe_call(lambda: get_vix_data(period=vix_period), demo_vix_data)
if vix_data["history"] is not None and len(vix_data["history"]) > 0:
    fig_vix = go.Figure()
    fig_vix.add_trace(go.Scatter(
        x=vix_data["history"].index,
        y=vix_data["history"]["Close"],
        mode="lines",
        name="VIX",
        line=dict(color="red"),
    ))
    fig_vix.add_hline(y=20, line_dash="dash", line_color="orange", annotation_text="Elevated (20)")
    fig_vix.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="High Fear (30)")
    fig_vix.update_layout(
        title="CBOE Volatility Index (VIX)",
        yaxis_title="VIX",
        height=350,
        margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig_vix, use_container_width=True)


# ---------------------------------------------------------------------------
# Row 4: Sector Performance
# ---------------------------------------------------------------------------
st.header("Sector Performance")
with st.spinner("Loading sectors..."):
    sectors_df, _ = safe_call(get_sector_performance, demo_sector_performance)

if not sectors_df.empty:
    tab1, tab2 = st.tabs(["Table", "Chart"])

    with tab1:
        st.dataframe(
            sectors_df.style.map(
                lambda v: "color: green" if isinstance(v, (int, float)) and v > 0
                else ("color: red" if isinstance(v, (int, float)) and v < 0 else ""),
                subset=["1D %", "1W %", "1M %"],
            ),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        fig_sectors = px.bar(
            sectors_df.sort_values("1D %"),
            x="1D %", y="Sector",
            orientation="h",
            color="1D %",
            color_continuous_scale=["red", "gray", "green"],
            color_continuous_midpoint=0,
            title="Today's Sector Performance",
        )
        fig_sectors.update_layout(height=400, margin=dict(t=40, b=20))
        st.plotly_chart(fig_sectors, use_container_width=True)


# ---------------------------------------------------------------------------
# Row 5: TradingView Heatmap Data
# ---------------------------------------------------------------------------
st.header("Stock Heatmap (Top by Market Cap)")
with st.spinner("Loading heatmap data from TradingView screener..."):
    heatmap_df, heatmap_demo = safe_call(get_tradingview_heatmap, demo_heatmap)

if not heatmap_df.empty:
    is_fallback = "_fallback" in heatmap_df.columns
    if is_fallback and not heatmap_demo:
        st.warning("Using fallback sector ETF data. Install `tradingview-screener` for full heatmap.")

    # Sector filter
    if "sector" in heatmap_df.columns:
        all_sectors = ["All"] + sorted(heatmap_df["sector"].dropna().unique().tolist())
        selected_sector = st.selectbox("Filter by Sector", all_sectors)
        if selected_sector != "All":
            heatmap_df = heatmap_df[heatmap_df["sector"] == selected_sector]

    # Treemap visualization
    if "change" in heatmap_df.columns and "market_cap_basic" in heatmap_df.columns:
        chart_df = heatmap_df.dropna(subset=["change", "market_cap_basic"]).copy()
        if not chart_df.empty:
            chart_df["change_capped"] = chart_df["change"].clip(-5, 5)
            chart_df["display_name"] = chart_df["name"]
            if "description" in chart_df.columns:
                chart_df["display_name"] = chart_df["name"] + " — " + chart_df["description"].fillna("")

            fig_tree = px.treemap(
                chart_df,
                path=["sector", "name"] if "sector" in chart_df.columns else ["name"],
                values="market_cap_basic",
                color="change_capped",
                color_continuous_scale=["#d32f2f", "#ffcdd2", "#e0e0e0", "#c8e6c9", "#388e3c"],
                color_continuous_midpoint=0,
                hover_data={"change": ":.2f", "close": ":.2f", "market_cap_basic": ":,.0f"},
                title="S&P 500 Heatmap — Size: Market Cap, Color: Daily Change %",
            )
            fig_tree.update_layout(height=600, margin=dict(t=40, b=20))
            st.plotly_chart(fig_tree, use_container_width=True)

    # Data table
    with st.expander("View Raw Data"):
        display_cols = [c for c in ["name", "description", "close", "change", "volume", "market_cap_basic", "sector"] if c in heatmap_df.columns]
        st.dataframe(heatmap_df[display_cols].head(50), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Row 6: Financial News
# ---------------------------------------------------------------------------
st.header("Market News")

if finnhub_key:
    with st.spinner("Loading news..."):
        news, news_demo = safe_call(lambda: get_market_news(finnhub_key), demo_news)
else:
    news, news_demo = demo_news(), True

for item in news[:15]:
    headline = item.get("headline", "")
    source = item.get("source", "")
    url = item.get("url", "")
    dt = item.get("datetime", "")
    summary = item.get("summary", "")

    with st.container():
        st.markdown(f"**[{headline}]({url})**")
        st.caption(f"{source} | {dt}")
        if summary:
            st.markdown(f"> {summary[:200]}..." if len(summary) > 200 else f"> {summary}")
        st.divider()

if not finnhub_key and not using_demo:
    st.info("Enter your Finnhub API key in the sidebar for live news. [Get a free key](https://finnhub.io/register)")

# Company-specific news lookup
if finnhub_key:
    st.subheader("Company News Lookup")
    symbol = st.text_input("Enter ticker symbol (e.g. AAPL, TSLA)")
    if symbol:
        with st.spinner(f"Loading news for {symbol.upper()}..."):
            company_news = get_company_news(symbol.upper(), finnhub_key)
        if company_news:
            for item in company_news:
                st.markdown(f"- [{item['headline']}]({item.get('url', '')})")
                st.caption(item.get("datetime", ""))
        else:
            st.info(f"No recent news found for {symbol.upper()}")


# ---------------------------------------------------------------------------
# Row 7: Fear & Greed Historical Context
# ---------------------------------------------------------------------------
if fg.get("score") is not None:
    st.header("Fear & Greed Context")
    fg_cols = st.columns(4)
    with fg_cols[0]:
        st.metric("Now", fg.get("score"))
    with fg_cols[1]:
        prev = fg.get("previous_close")
        st.metric("Previous Close", prev if prev else "N/A")
    with fg_cols[2]:
        week = fg.get("one_week_ago")
        st.metric("1 Week Ago", week if week else "N/A")
    with fg_cols[3]:
        month = fg.get("one_month_ago")
        st.metric("1 Month Ago", month if month else "N/A")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Data is delayed and for informational purposes only. Not financial advice. "
    "Sources: yfinance, TradingView Screener, Finnhub, CNN Fear & Greed, CBOE."
)
