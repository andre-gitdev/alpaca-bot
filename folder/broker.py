"""Alpaca broker service that wraps REST and streaming clients."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Iterable

from alpaca.data import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
'''from alpaca.trading.stream import AccountUpdates'''

from config import AlpacaCredentials, StrategyConfig


class AlpacaBroker:
    """Facade over Alpaca trading and market-data clients."""

    def __init__(self, credentials: AlpacaCredentials, strategy: StrategyConfig):
        self._strategy = strategy
        self._trading = TradingClient(
            api_key=credentials.key_id,
            secret_key=credentials.secret_key,
            paper=credentials.paper,
        )
        self._data = StockHistoricalDataClient(
            credentials.key_id, credentials.secret_key
        )
        self._stream = StockDataStream(
            credentials.key_id, credentials.secret_key, paper=credentials.paper
        )

    # ------------------------------------------------------------------
    # Trading REST operations
    def get_account(self):
        return self._trading.get_account()

    def get_positions(self):
        return {pos.symbol: pos for pos in self._trading.get_all_positions()}

    def get_position(self, symbol: str):
        try:
            return self._trading.get_open_position(symbol)
        except Exception:  # Alpaca raises APIError when no position exists
            return None

    def submit_market_order(self, *, symbol: str, qty: int, side: OrderSide,
                             time_in_force: TimeInForce) -> Any:
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force,
        )
        return self._trading.submit_order(request)

    def close_position(self, symbol: str):
        try:
            self._trading.close_position(symbol)
        except Exception:
            pass

    def close_all_positions(self):
        try:
            self._trading.close_all_positions(cancel_orders=True)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Market data REST operations
    def get_seed_bars(self, symbol: str, limit: int) -> list:
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute,
            limit=limit,
        )
        bars = self._data.get_stock_bars(request)
        if hasattr(bars, "data"):
            return list(bars.data.get(symbol, []))
        if isinstance(bars, dict):
            return list(bars.get(symbol, []))
        if isinstance(bars, Iterable):
            return list(bars)
        return []

    # ------------------------------------------------------------------
    # Streaming interface
    def subscribe_bars(self, handler: Callable[[Any], Awaitable[None]], *symbols: str):
        self._stream.subscribe_bars(handler, *symbols)

    '''def subscribe_account_updates(self, handler: Callable[[AccountUpdates], Awaitable[None]]):
        self._stream.subscribe_trade_updates(handler)'''

    async def run_stream(self):
        await self._stream.run()

    async def stop_stream(self):
        await self._stream.stop()

    async def ensure_stream_running(self):
        if self._stream._running:  # type: ignore[attr-defined]
            return
        await self._stream.run()

    # ------------------------------------------------------------------
    # Utility helpers
    def to_time_in_force(self, value: str) -> TimeInForce:
        return TimeInForce(value.upper())

    @property
    def strategy(self) -> StrategyConfig:
        return self._strategy

    @property
    def stream(self) -> StockDataStream:
        return self._stream
