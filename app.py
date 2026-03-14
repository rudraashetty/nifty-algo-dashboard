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

# 1. INITIALIZE MODULES (Moved to top to prevent scope errors)
@st.cache_resource
def init_modules():
    from trading_logic import DataFetcher, DiscordNotifier, PredictiveModel, BacktestEngine
    return DataFetcher(), DiscordNotifier(webhook_url=""), PredictiveModel(), BacktestEngine()

fetcher, notifier, ml_model, backtest_engine = init_modules()

# 2. PAGE CONFIGURATION
st.set_page_config(page_title="NIFTY 50 Algo Dashboard", layout="wide", page_icon="📈")

def get_market_sentiment(text):
    if not text: return 0.0
    return round(TextBlob(text).sentiment.polarity, 2)

# 3. HEADER
st.markdown(f"""
    <div style="text-align: center; padding: 10px; border-bottom: 2px solid #4CAF50; margin-bottom: 20px;">
        <h1 style="color: #4CAF50; margin-bottom: 0;">📈 Dev Canvas Trading Engine</h1>
        <p style="font-size: 1.2em; color: #888;">Developed by <b>Rudra Shetty</b> | AI & ML Specialist</p>
    </div>
""", unsafe_allow_html=True)

# 4. SIDEBAR
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go To:", ["Live Tracker", "Signal Database"])

if st.sidebar.button("🧪 Log Test Signal"):
    try:
        score = get_market_sentiment("NIFTY-50 is showing strong bullish momentum.")
        db_manager.log_signal(ticker="NIFTY 50", signal_type="BUY", price=25000.0, sentiment=score, timeframe="5m")
        st.sidebar.success(f"Logged! AI Mood: {score}")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# 5. MAIN LOGIC
if app_mode == "Live Tracker":
    st.header("🔴 Live Intraday Tracker")
    if st.button("Fetch Latest Data"):
        df = fetcher.fetch_live_data(ticker="^NSEI", interval="5m")
        if not df.empty:
            st.line_chart(df['Close'])

elif app_mode == "Signal Database":
    st.header("🗄️ SQL Database Logs")
    signals = db_manager.get_recent_signals()
    if signals:
        st.table([{"Type": s.signal_type, "Price": s.price, "Mood": getattr(s, 'sentiment_score', 0.0)} for s in signals])
    else:
        st.info("No data yet.")
