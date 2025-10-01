"""Configuration objects for Alpaca trading strategies."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time, timedelta
from typing import List, Sequence


@dataclass(slots=True)
class StreamConfig:
    """Settings for the market data stream."""

    symbols: Sequence[str] = field(default_factory=lambda: ["SOXL"])
    reconnect_delay: float = 5.0


@dataclass(slots=True)
class RiskConfig:
    """Risk management parameters for the strategy."""

    max_position_age: timedelta = timedelta(hours=6)
    close_all_at: time | None = time(hour=15, minute=55)
    buying_power_timeout: timedelta = timedelta(seconds=30)
    buying_power_poll_interval: float = 2.0


@dataclass(slots=True)
class IndicatorConfig:
    """Indicator lookback windows and behaviour."""

    ema_period: int = 10
    sma_period: int = 50
    atr_period: int = 14
    seed_bars: int = 100


@dataclass(slots=True)
class AllocationConfig:
    """Settings used to derive order quantities."""

    cash_fraction: float = 0.9
    order_time_in_force: str = "day"


@dataclass(slots=True)
class StrategyConfig:
    """Bundle of configuration used by the EMA/SMA strategy."""

    bullish_symbol: str = "SOXL"
    bearish_symbol: str = "SOXS"
    stream: StreamConfig = field(default_factory=StreamConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    indicators: IndicatorConfig = field(default_factory=IndicatorConfig)
    allocation: AllocationConfig = field(default_factory=AllocationConfig)

    def all_symbols(self) -> List[str]:
        symbols: List[str] = list(dict.fromkeys(
            [self.bullish_symbol, self.bearish_symbol, *self.stream.symbols]
        ))
        return symbols


@dataclass(slots=True)
class AlpacaCredentials:
    """Container for Alpaca API credentials."""

    key_id: str
    secret_key: str
    paper: bool = True

    @classmethod
    def from_env(cls) -> "AlpacaCredentials":
        import os

        key_id = os.environ["ALPACA_K"]
        secret_key = os.environ["ALPACA_SK"]
        paper = os.environ.get("ALPACA_PAPER", "true").lower() != "false"
        return cls(key_id=key_id, secret_key=secret_key, paper=paper)


@dataclass(slots=True)
class AppConfig:
    """Top-level configuration for the trading application."""

    credentials: AlpacaCredentials
    strategy: StrategyConfig = field(default_factory=StrategyConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(credentials=AlpacaCredentials.from_env())
