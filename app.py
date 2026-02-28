import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

try:
    from database import db_manager
    from trading_logic import DataFetcher, TechnicalIndicators, BacktestEngine, DiscordNotifier, PredictiveModel
except ImportError as e:
    st.error(f"Critical Dependency Error: {e}")
    st.stop()

st.set_page_config(page_title="NIFTY 50 Algo Dashboard", layout="wide", page_icon="📈")
# --- CUSTOM HEADER & BRANDING ---
st.markdown(f"""
    <div style="text-align: center; padding: 10px; border-bottom: 2px solid #4CAF50; margin-bottom: 30px;">
        <h1 style="color: #4CAF50; margin-bottom: 0;">Dev Canvas Trading Engine</h1>
        <p style="font-size: 1.2em; color: #888;">Developed by <b>Rudra Shetty</b> | Intelligent Market Analysis</p>
    </div>
""", unsafe_allow_html=True)
# --- THEME SELECTION ---
theme_choice = st.sidebar.select_slider(
    "Select Dashboard Theme",
    options=["Professional Dark", "Light Mode"],
    value="Professional Dark"
)

if theme_choice == "Professional Dark":
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: white; }
        </style>
    """, unsafe_allow_html=True)
@st.cache_resource
def init_modules():
    return DataFetcher(), DiscordNotifier(webhook_url=""), PredictiveModel()

fetcher, notifier, ml_model = init_modules()

st.sidebar.title("System Navigation")
app_mode = st.sidebar.radio("Select Module:", ["Live Intraday Tracker", "Backtesting Engine", "Signal Database"])

st.sidebar.markdown("---")
st.sidebar.subheader("Alert Settings")

# 1. This looks for the secret you saved in the Cloud settings first
cloud_secret = st.secrets.get("DISCORD_WEBHOOK_URL", "")

# 2. This shows the input box, pre-filled with your secret URL
discord_url = st.sidebar.text_input("Discord Webhook URL", value=cloud_secret, type="password")

# 3. If there is a URL (from the secret or typed in), show the button
if discord_url:
    notifier.webhook_url = discord_url
    if st.sidebar.button("🔔 Send Test Alert"):
        notifier.send_alert("🤖 Dev Canvas Trading Bot is successfully connected!")
        st.sidebar.success("Test alert sent to Discord!")
import segno
import io

st.sidebar.markdown("---")
st.sidebar.subheader("Share App")

# 1. Create the QR code linking to your current URL
# (Streamlit automatically knows its own URL)
app_url = "https://nifty-algo-dashboard-hmnn6kvm3sjpw4us6gbvmo.streamlit.app/" # Replace with your actual URL
qr = segno.make(app_url)

# 2. Save it to a buffer so Streamlit can display it
buf = io.BytesIO()
qr.save(buf, kind='png', scale=4)
st.sidebar.image(buf.getvalue(), caption="Scan to open on Mobile")
st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Risk Calculator")

# 1. User Inputs for Risk Management
capital = st.sidebar.number_input("Total Trading Capital (₹)", value=100000, step=1000)
risk_percent = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)
entry_price = st.sidebar.number_input("Entry Price (₹)", value=0.0)
stop_loss = st.sidebar.number_input("Stop Loss (₹)", value=0.0)

# 2. Logic to calculate quantity
if entry_price > 0 and stop_loss > 0 and entry_price > stop_loss:
    amount_to_risk = capital * (risk_percent / 100)
    risk_per_share = entry_price - stop_loss
    quantity = int(amount_to_risk / risk_per_share)
    
    st.sidebar.success(f"Risk Amount: ₹{amount_to_risk:.2f}")
    st.sidebar.info(f"Recommended Quantity: {quantity} shares")
    st.sidebar.warning(f"Total Trade Value: ₹{quantity * entry_price:.2f}")
elif entry_price <= stop_loss and entry_price > 0:
    st.sidebar.error("Stop Loss must be below Entry Price for a Buy trade.")
def plot_advanced_chart(df: pd.DataFrame, ticker: str):
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2], 
        subplot_titles=(f"{ticker} Price", "RSI (14)", "MACD"),
        specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # 1. Main Price & Bollinger Bands
    fig.add_trace(go.Candlestick(x=df['Datetime'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['BB_Upper'], name='BB Upper', line=dict(color='rgba(173, 216, 230, 0.4)', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['BB_Lower'], name='BB Lower', line=dict(color='rgba(173, 216, 230, 0.4)', width=1), fill='tonexty', fillcolor='rgba(173, 216, 230, 0.1)'), row=1, col=1)

    # 2. Volume (Properly Scaled)
    if 'Volume' in df.columns:
        fig.add_trace(go.Bar(x=df['Datetime'], y=df['Volume'], name='Volume', marker_color='rgba(128, 128, 128, 0.4)'), row=1, col=1, secondary_y=True)

    # 3. RSI
    if 'RSI_14' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['RSI_14'].fillna(50), name="RSI", line=dict(color='purple')), row=2, col=1)fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['MACD'].fillna(0), name="MACD", line=dict(color='blue')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['MACD_Signal'].fillna(0), name="Signal", line=dict(color='orange')), row=3, col=1)
        fig.add_trace(go.Bar(x=df['Datetime'], y=df['MACD_Hist'].fillna(0), name="Histogram"), row=3, col=1)

    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

if app_mode == "Live Intraday Tracker":
    st.title("🔴 Live Intraday Tracker")
    
    # 1. New Dropdown for Assets
    ticker_choice = st.selectbox("Select Asset", 
                                ["NIFTY 50 (^NSEI)", "RELIANCE (RELIANCE.NS)", "TCS (TCS.NS)", "HDFC BANK (HDFCBANK.NS)"])
    
    # 2. Extract the symbol correctly
    selected_ticker = ticker_choice.split("(")[1].replace(")", "")
    
    timeframe = st.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h"], index=1)
    
    if st.button("Refresh Market Data"):
        with st.spinner(f"Fetching Live Data for {selected_ticker}..."):
            # Use the selected_ticker variable here
            raw_df = fetcher.fetch_live_data(ticker=selected_ticker, interval=timeframe)
            
            # The code below must be indented exactly 12 spaces (3 tabs) from the left
            if raw_df is not None and not raw_df.empty:
                df = TechnicalIndicators.add_all_indicators(raw_df)
                latest = df.iloc[-1]
                
                # Metrics Display
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Current Price", f"₹{latest['Close']:.2f}")
                m2.metric("RSI (14)", f"{latest.get('RSI_14', 50):.2f}")
                m3.metric("MACD", f"{latest.get('MACD', 0):.2f}")
                m4.metric("AI Bullish Confidence", f"{ml_model.predict_confidence(df)}%")
                
                plot_advanced_chart(df, ticker_choice.split(" (")[0])
                
                rsi_val = latest.get('RSI_14', 50)
                if pd.notna(rsi_val):
                    if rsi_val > 70:
                        st.warning("⚠️ Overbought Signal Detected!")
                        db_manager.log_signal("NIFTY50", "SELL", latest['Close'], timeframe, {"RSI": rsi_val})
                        notifier.send_alert(f"🔴 *SELL ALERT* NIFTY50\nPrice: ₹{latest['Close']}\nRSI: {rsi_val:.2f}")
                    elif rsi_val < 30:
                        st.success("✅ Oversold Signal Detected!")
                        db_manager.log_signal("NIFTY50", "BUY", latest['Close'], timeframe, {"RSI": rsi_val})
                        notifier.send_alert(f"🟢 *BUY ALERT* NIFTY50\nPrice: ₹{latest['Close']}\nRSI: {rsi_val:.2f}")
            else:
                st.error("Failed to fetch market data.")

elif app_mode == "Backtesting Engine":
    st.title("⚙️ Algorithmic Backtesting Engine")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", datetime(2023, 1, 1))
    end_date = col2.date_input("End Date", datetime.now())
    
    if st.button("Run Backtest"):
        with st.spinner("Crunching historical data..."):
            hist_df = fetcher.fetch_historical_data(start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
            if hist_df is not None:
                df_with_inds = TechnicalIndicators.add_all_indicators(hist_df)
                results = BacktestEngine.run_macd_crossover(df_with_inds)
                
                st.subheader("Results (MACD Crossover)")
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Total Trades", results['total_trades'])
                r2.metric("Win Rate", f"{results['win_rate']}%")
                r3.metric("Max Drawdown", f"{results['max_drawdown']}%")
                r4.metric("Total Return", f"{results['total_return']}%")
                
                db_manager.log_backtest_result("MACD Crossover", "NIFTY50", "1d", results['total_trades'], results['win_rate'], results['max_drawdown'], results['total_return'])

elif app_mode == "Signal Database":
    st.title("🗄️ SQL Database Logs")
    tab1, tab2 = st.tabs(["Recent Signals", "Backtest History"])
    with tab1:
        signals = db_manager.get_recent_signals()
        if signals: st.dataframe(pd.DataFrame([s.to_dict() for s in signals]), use_container_width=True)
    with tab2:
        logs = db_manager.get_backtest_history()
        if logs: st.dataframe(pd.DataFrame([l.to_dict() for l in logs]), use_container_width=True)
# --- ADVANCED TECHNICAL INDICATORS (Professional Upgrade) ---
class TechnicalIndicators:
    @staticmethod
    def add_rsi(df, window=14):
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def add_macd(df):
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        return df

    @staticmethod
    def add_bollinger_bands(df, window=20, num_std=2):
        rolling_mean = df['Close'].rolling(window=window).mean()
        rolling_std = df['Close'].rolling(window=window).std()
        df['BB_Middle'] = rolling_mean
        df['BB_Upper'] = rolling_mean + (rolling_std * num_std)
        df['BB_Lower'] = rolling_mean - (rolling_std * num_std)
        return df

    @staticmethod
    def add_volume_ma(df, window=20):
        df['Vol_MA'] = df['Volume'].rolling(window=window).mean()
        return df

    @classmethod
    def add_all_indicators(cls, df):
        df = cls.add_rsi(df)
        df = cls.add_macd(df)
        df = cls.add_bollinger_bands(df)
        df = cls.add_volume_ma(df)
        return df
