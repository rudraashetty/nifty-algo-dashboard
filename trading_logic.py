import pandas as pd
import ta
import yfinance as yf
import numpy as np
import threading
import requests
import logging
from sklearn.preprocessing import StandardScaler

class TechnicalIndicators:
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or len(df) < 200: return df
        # MACD & RSI
        df['RSI_14'] = ta.momentum.rsi(df['Close'], window=14)
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        # The Filter: 200-day EMA
        df['EMA_200'] = ta.trend.ema_indicator(df['Close'], window=200)
        return df

class BacktestEngine:
    @staticmethod
    def run_macd_crossover(df: pd.DataFrame):
        # Logic: Buy only if MACD Crosses UP AND Price > EMA_200
        df['Signal'] = np.where((df['MACD'] > df['MACD_Signal']) & (df['Close'] > df['EMA_200']), 1, 0)
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        
        trades = df[df['Signal'].diff() != 0]
        win_rate = (df['Strategy_Returns'] > 0).sum() / len(df[df['Strategy_Returns'] != 0]) * 100
        total_return = (np.exp(np.log1p(df['Strategy_Returns']).sum()) - 1) * 100
        
        return {
            "total_trades": len(trades),
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(df['Strategy_Returns'].min() * 100, 2),
            "total_return": round(total_return, 2)
        }
# ... (rest of the classes remain the same)
