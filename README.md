# 💹 Dev Canvas Trading Engine: NIFTY-50 Analytics
### **Developed by Rudra Shetty**
**B.E. Computer Science (CS-IOT & CyberSecurity also an AI tools Enthusiast)**
*Mangalore Institute of Technology & Engineering (MITE)*

---

## 🌟 Overview
The **Dev Canvas Trading Engine** is a sophisticated, full-stack financial dashboard designed for real-time **NIFTY-50** market analysis. It leverages **Python** and **SQLAlchemy** to bridge the gap between live market data and persistent performance tracking.

---

## 🚀 Core Features
* **📡 Live Intraday Tracker**: Real-time candle charts with automated **MACD Bullish/Bearish** crossover detection.
* **📊 SQL Analytics Suite**: Persistent logging of every trade signal using a robust **PostgreSQL/SQLite** backend.
* **📈 Performance Dashboard**: Interactive metrics calculating **Total Trades**, **Buy/Sell Ratios**, and daily activity trends.
* **⚖️ Advanced Risk Management**: Built-in calculator for **Position Sizing** based on custom capital and risk-per-trade.
* **🧠 Predictive Indicators**: Multi-indicator validation using **Bollinger Bands (20, 2)** and **RSI (14)**.

---

## 🛠️ Technical Stack
| Category | Technology |
| :--- | :--- |
| **Frontend** | **Streamlit** (Interactive Web UI) |
| **Backend** | **Python** & **SQLAlchemy ORM** |
| **Database** | **PostgreSQL** (Production) / **SQLite** (Dev) |
| **Analysis** | **Pandas**, **NumPy**, **yfinance** |
| **Visuals** | **Plotly** (Multi-axis Candlestick Charts) |

---

## 🏗️ Architectural Engineering
To ensure high availability, this project solves several common production challenges:
1. **Memory Persistence**: Implements `expire_on_commit=False` in the SQLAlchemy session to prevent `DetachedInstanceError` during high-frequency UI updates.
2. **Schema Stability**: Uses a "Safe-Fetch" layer with Python's `getattr` to ensure the UI never crashes if the database schema evolves.
3. **Real-time Concurrency**: Optimized for the **Streamlit** execution model to handle live price streams alongside database writes.

---

## 📁 Repository Structure
* `app.py`: Main dashboard logic and UI components.
* `database.py`: SQL models and automated `DatabaseManager`.
* `trading_logic.py`: Vectorized technical indicators and backtest engine.

---

## 🎓 About the Developer
I am a **7th-semester B.E. student** specializing in **Artificial Intelligence and Machine Learning**. My portfolio includes **NeuroVocal AI** (Deep Learning for Disease Detection) and **AuditFlow** (Automated Technical Debt Auditor). I am currently applying my skills as an intern at **Reverse Engineering Infotec**.

---
