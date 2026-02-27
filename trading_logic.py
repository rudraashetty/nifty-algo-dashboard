import pandas as pd
import ta
import yfinance as yf
import numpy as np
import threading
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def fetch_live_data(self, ticker: str = "^NSEI", interval: str = "5m") -> Optional[pd.DataFrame]:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d", interval=interval)
            if df.empty: return None
            df = df.dropna().reset_index()
            return df
        except Exception as e:
            logger.error(f"Market fetch error: {e}")
            return None

    def fetch_historical_data(self, ticker: str = "^NSEI", start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        try:
            if not start_date: start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date: end_date = datetime.now().strftime('%Y-%m-%d')
            df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
            if df.empty: return None
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df.dropna().reset_index()
        except Exception as e:
            logger.error(f"Historical fetch error: {e}")
            return None

class TechnicalIndicators:
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or len(df) < 200: return df
        df['RSI_14'] = ta.momentum.rsi(df['Close'], window=14)
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        df['EMA_200'] = ta.trend.ema_indicator(df['Close'], window=200)
        return df

class BacktestEngine:
    @staticmethod
    def run_macd_crossover(df: pd.DataFrame):
        if df is None or 'EMA_200' not in df.columns:
            return {"total_trades": 0, "win_rate": 0.0, "max_drawdown": 0.0, "total_return": 0.0}
        
        df['Signal'] = np.where((df['MACD'] > df['MACD_Signal']) & (df['Close'] > df['EMA_200']), 1, 0)
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        
        trades = df[df['Signal'].diff() != 0]
        active_returns = df[df['Strategy_Returns'] != 0]['Strategy_Returns']
        
        win_rate = (active_returns > 0).sum() / len(active_returns) * 100 if len(active_returns) > 0 else 0
        total_return = (np.exp(np.log1p(df['Strategy_Returns']).sum()) - 1) * 100
        
        return {
            "total_trades": len(trades),
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(df['Strategy_Returns'].min() * 100, 2),
            "total_return": round(total_return, 2)
        }

class DiscordNotifier:
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    def _send_request(self, message: str):
        if not self.webhook_url: return
        payload = {"content": message}
        try:
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Discord Error: {e}")

    def send_alert(self, message: str):
        thread = threading.Thread(target=self._send_request, args=(message,), daemon=True)
        thread.start()

class PredictiveModel:
    def __init__(self):
        self.scaler = StandardScaler()

    def predict_confidence(self, df: pd.DataFrame) -> float:
        try:
            if df is None or len(df) < 10: return 50.0
            features = df[['Open', 'High', 'Low', 'Close']].tail(10).dropna()
            if features.empty: return 50.0
            scaled_features = self.scaler.fit_transform(features)
            recent_momentum = scaled_features[-1][3] - scaled_features[0][3]
            confidence = 50.0 + (recent_momentum * 10)
            return round(min(max(confidence, 0.0), 100.0), 2)
        except Exception:
            return 50.0
