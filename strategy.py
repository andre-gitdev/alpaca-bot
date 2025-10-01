"""EMA/SMA crossover trading strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from alpaca.data.models import Bar
from alpaca.trading.enums import OrderSide

from indicators import IndicatorSet
from risk import RiskManager

if TYPE_CHECKING:  # pragma: no cover - import only for type checkers
    from broker import AlpacaBroker


class EmaSmaStrategy:
    """Implements the SOXL/SOXS crossover logic from the notebook."""

    def __init__(self, broker: "AlpacaBroker", indicators: IndicatorSet, risk: RiskManager):
        self._broker = broker
        self._config = broker.strategy
        self._indicators = indicators
        self._risk = risk

    async def on_bar(self, bar: Bar):
        self._indicators.update_from_bar(bar)

        ema = self._indicators.latest_ema
        sma = self._indicators.latest_sma
        if ema is None or sma is None:
            return

        # Flatten positions when approaching the configured cutoff.
        if self._risk.should_flatten_positions(self._timestamp_to_datetime(bar.timestamp)):
            self._risk.flatten_positions()
            return

        if ema > sma:
            await self._enter_symbol(
                target_symbol=self._config.bullish_symbol,
                hedge_symbol=self._config.bearish_symbol,
                last_price=bar.close,
                side=OrderSide.BUY,
            )
        elif ema < sma:
            await self._enter_symbol(
                target_symbol=self._config.bearish_symbol,
                hedge_symbol=self._config.bullish_symbol,
                last_price=bar.close,
                side=OrderSide.BUY,
            )

    async def _enter_symbol(self, *, target_symbol: str, hedge_symbol: str, last_price: float, side: OrderSide) -> None:
        await self._risk.ensure_no_opposite_position(hedge_symbol)

        account = self._broker.get_account()
        buying_power = float(account.buying_power)
        allocation = buying_power * self._config.allocation.cash_fraction
        quantity = int(allocation // last_price)
        if quantity <= 0:
            return

        if not await self._risk.wait_for_buying_power(quantity * last_price):
            return

        existing_position = self._broker.get_position(target_symbol)
        if existing_position and int(float(existing_position.qty)) > 0:
            return

        self._broker.submit_market_order(
            symbol=target_symbol,
            qty=quantity,
            side=side,
            time_in_force=self._broker.to_time_in_force(self._config.allocation.order_time_in_force),
        )

    @staticmethod
    def _timestamp_to_datetime(ts) -> Optional[datetime]:
        if ts is None:
            return None
        if isinstance(ts, datetime):
            return ts
        try:
            return datetime.fromisoformat(str(ts))
        except Exception:
            return None
