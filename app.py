import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
from database import db_manager
from textblob import TextBlob
import io
import segno

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="NIFTY 50 Algo Dashboard", layout="wide", page_icon="📈")

# 2. SENTIMENT ANALYSIS CORE
def get_market_sentiment(text):
    """Analyzes text and returns a score between -1.0 and 1.0."""
    if not text:
        return 0.0
    analysis = TextBlob(text)
    return round(analysis.sentiment.polarity, 2)

# 3. CUSTOM HEADER & BRANDING
st.markdown(f"""
    <div style="text-align: center; padding: 10px; border-bottom: 2px solid #4CAF50; margin-bottom: 20px;">
        <h1 style="color: #4CAF50; margin-bottom: 0;">📈 Dev Canvas Trading Engine</h1>
        <p style="font-size: 1.2em; color: #888;">Developed by <b>Rudra Shetty</b> | Intelligent Market Analytics</p>
    </div>
""", unsafe_allow_html=True)

# 4. INITIALIZE MODULES
@st.cache_resource
def init_modules():
    # Note: These classes must be defined in your other files (trading_logic.py, etc.)
    from trading_logic import DataFetcher, DiscordNotifier, PredictiveModel, BacktestEngine
    return DataFetcher(), DiscordNotifier(webhook_url=""), PredictiveModel(), BacktestEngine

fetcher, notifier, ml_model, backtest_engine = init_modules()

# 5. SIDEBAR NAVIGATION
st.sidebar.title("System Navigation")
app_mode = st.sidebar.radio("Select Module:", ["Live Intraday Tracker", "Backtesting Engine", "Signal Database"])

# 6. SIDEBAR: RISK CALCULATOR
st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Risk Calculator")
capital = st.sidebar.number_input("Total Trading Capital (₹)", value=100000, step=1000)
risk_percent = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)
entry_price = st.sidebar.number_input("Entry Price (₹)", value=100.0)
stop_loss = st.sidebar.number_input("Stop Loss (₹)", value=95.0)

if entry_price > stop_loss > 0:
    amount_to_risk = capital * (risk_percent / 100)
    risk_per_share = entry_price - stop_loss
    quantity = int(amount_to_risk / risk_per_share)
    st.sidebar.success(f"Recommended Quantity: {quantity} shares")
else:
    st.sidebar.warning("Ensure Entry > Stop Loss")

# 7. SIDEBAR: AI TOOLS & DATABASE CONTROLS
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Developer Tools")
if st.sidebar.button("🧪 Log Test Signal"):
    try:
        test_headline = "NIFTY-50 hits record high as global markets rally on positive earnings."
        score = get_market_sentiment(test_headline)
        db_manager.log_signal(
            ticker="NIFTY 50",
            signal_type="BUY",
            price=25181.80,
            sentiment=score,
            timeframe="5m"
        )
        st.sidebar.success(f"Signal Logged! AI Mood: {score}")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Test Log Failed: {e}")

if st.sidebar.button("🗑️ Clear All Test Data"):
    try:
        db_manager.clear_all_data()
        st.sidebar.warning("All database logs deleted!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Clear Failed: {e}")

# 8. THE CHARTING FUNCTION
def plot_advanced_chart(df, ticker):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    
    if 'RSI_14' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], name="RSI", line=dict(color='purple')), row=2, col=1)
    
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='blue')), row=3, col=1)
        
    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# 9. MAIN PAGE MODULES
if app_mode == "Live Intraday Tracker":
    st.title("🔴 Live Intraday Tracker")
    ticker_choice = st.selectbox("Select Asset", ["NIFTY 50 (^NSEI)", "RELIANCE (RELIANCE.NS)"])
    selected_ticker = ticker_choice.split("(")[1].replace(")", "")
    
    if st.button("Refresh Market Data"):
        with st.spinner("Fetching Data..."):
            df = fetcher.fetch_live_data(ticker=selected_ticker, interval="5m")
            if not df.empty:
                from trading_logic import TechnicalIndicators
                df = TechnicalIndicators.add_all_indicators(df)
                plot_advanced_chart(df, selected_ticker)

elif app_mode == "Signal Database":
    st.title("🗄️ SQL Database Logs")
    signals = db_manager.get_recent_signals()
    if signals:
        signal_data = []
        for s in signals:
            signal_data.append({
                "Ticker": getattr(s, 'ticker', 'N/A'),
                "Type": getattr(s, 'signal_type', 'N/A'),
                "Price": getattr(s, 'price', 0.0),
                "AI Mood": getattr(s, 'sentiment_score', 0.0),
                "Time": getattr(s, 'timestamp', 'N/A')
            })
        st.dataframe(pd.DataFrame(signal_data), use_container_width=True)
    else:
        st.info("No signals logged yet.")

# --- TECHNICAL INDICATORS CLASS ---
class TechnicalIndicators:
    @staticmethod
    def add_all_indicators(df):
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI_14'] = 100 - (100 / (1 + (gain / loss)))
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        return df
