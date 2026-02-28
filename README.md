📈 Dev Canvas Trading Engine: NIFTY-50 Intraday Analytics
Developed by Rudra Shetty | AI & Machine Learning Specialization

A high-performance, full-stack trading dashboard built with Streamlit and SQLAlchemy for real-time intraday market analysis and automated signal logging. This engine integrates technical indicators with a robust database backend to track trading performance over time.

🚀 Key Features
Live Intraday Tracker: Real-time Nifty-50 data visualization with automated MACD Bullish/Bearish Crossover detection.

Predictive Analytics: Integrated technical indicators including Bollinger Bands (20, 2) and RSI (14) for trend strength validation.

SQL Database Logs: Persistent storage for all generated signals and backtest results using PostgreSQL (Production) and SQLite (Development).

Daily Performance Summary: Interactive UI cards and charts that calculate total trades, buy/sell ratios, and daily activity trends.

Risk Management Suite: A built-in calculator that determines optimal Position Sizing based on custom capital and risk percentages.

💻 Technical Stack
Frontend: Streamlit (Python-based Web Framework).

Backend & Database: SQLAlchemy ORM for robust database session management and signal persistence.

Data Processing: Pandas & NumPy for vectorized technical indicator calculations.

Visualization: Plotly for interactive, multi-axis candlestick charting.

Real-time Data: Integrated via yfinance for high-fidelity market snapshots.

🛠️ Architecture Highlights
To ensure production stability, this engine utilizes a non-expiring database session (expire_on_commit=False) to prevent DetachedInstanceError during high-frequency data reads. It also features a "Safe-Check" data extraction layer using getattr to maintain UI stability even with evolving database schemas.

📁 Project Structure
Plaintext
├── app.py              # Main Streamlit UI and Module Logic
├── database.py         # SQLAlchemy Models and DatabaseManager Class
├── trading_logic.py    # Indicator classes and Backtest Engine
├── requirements.txt    # Project dependencies
└── trading_dashboard.db# Local SQLite development database
🎓 Academic & Professional Context
This project was developed as part of my 7th-semester BE in Computer Science (AI & ML) at Mangalore Institute of Technology & Engineering (MITE). It builds upon my previous experience developing AuditFlow (Technical Debt Auditor) and NeuroVocal AI (Deep Learning for Disease Classification).
