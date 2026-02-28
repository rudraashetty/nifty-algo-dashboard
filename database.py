"""
database.py
SQLAlchemy setup optimized for PostgreSQL in production, with SQLite fallback for local testing.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trading_dashboard.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()

class TradingSignal(Base):
    __tablename__ = 'trading_signals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    ticker = Column(String(20), nullable=False)
    signal_type = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    timeframe = Column(String(10), nullable=True)
    indicator_values = Column(Text, nullable=True)
    status = Column(String(20), default='ACTIVE')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ticker': self.ticker,
            'signal_type': self.signal_type,
            'price': self.price,
            'timeframe': self.timeframe,
            'status': self.status
        }

class BacktestLog(Base):
    __tablename__ = 'backtest_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    strategy_name = Column(String(50), nullable=False)
    ticker = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    total_trades = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'strategy_name': self.strategy_name,
            'ticker': self.ticker,
            'win_rate': self.win_rate,
            'total_return': self.total_return
        }

class DatabaseManager:
    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        try:
            engine_kwargs = {}
            if "sqlite" in self.database_url:
                engine_kwargs["connect_args"] = {'check_same_thread': False}
            else:
                engine_kwargs["pool_size"] = 5
                engine_kwargs["max_overflow"] = 10

            self.engine = create_engine(self.database_url, **engine_kwargs)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def log_signal(self, ticker: str, signal_type: str, price: float, timeframe: str = None, indicator_values: Dict = None):
        try:
            with self.get_session() as session:
                signal = TradingSignal(
                    ticker=ticker, signal_type=signal_type.upper(), price=price,
                    timeframe=timeframe, indicator_values=json.dumps(indicator_values) if indicator_values else None
                )
                session.add(signal)
        except SQLAlchemyError as e:
            logger.error(f"DB Log Error: {e}")

    def log_backtest_result(self, strategy: str, ticker: str, timeframe: str, trades: int, win_rate: float, max_dd: float, total_ret: float):
        try:
            with self.get_session() as session:
                log = BacktestLog(
                    strategy_name=strategy, ticker=ticker, timeframe=timeframe,
                    total_trades=trades, win_rate=win_rate, max_drawdown=max_dd, total_return=total_ret
                )
                session.add(log)
        except SQLAlchemyError as e:
            logger.error(f"DB Log Error: {e}")

    def get_recent_signals(self, limit: int = 50):
        with self.get_session() as session:
            return session.query(TradingSignal).order_by(TradingSignal.timestamp.desc()).limit(limit).all()

    def get_backtest_history(self, limit: int = 20):
        with self.get_session() as session:
            return session.query(BacktestLog).order_by(BacktestLog.timestamp.desc()).limit(limit).all()

db_manager = DatabaseManager()
