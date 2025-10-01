"""Risk management helpers used by the trading strategy."""
from __future__ import annotations

import asyncio
from datetime import datetime, time
from typing import Optional

from alpaca.trading.enums import OrderSide

from config import RiskConfig


class RiskManager:
    """Collection of risk-related checks and routines."""

    def __init__(self, broker, config: RiskConfig):
        self._broker = broker
        self._config = config

    async def wait_for_buying_power(self, required_cash: float) -> bool:
        """Poll the account until buying power covers the required cash."""
        loop = asyncio.get_event_loop()
        deadline = loop.time() + self._config.buying_power_timeout.total_seconds()
        while loop.time() < deadline:
            account = self._broker.get_account()
            if float(account.buying_power) >= required_cash:
                return True
            await asyncio.sleep(self._config.buying_power_poll_interval)
        return False

    def should_flatten_positions(self, now: Optional[datetime] = None) -> bool:
        if self._config.close_all_at is None:
            return False
        now = now or datetime.now()
        cutoff = self._config.close_all_at
        return time(now.hour, now.minute) >= cutoff

    def flatten_positions(self):
        self._broker.close_all_positions()

    async def ensure_no_opposite_position(self, hedge_symbol: str):
        hedge_position = self._broker.get_position(hedge_symbol)
        if hedge_position:
            qty = int(float(hedge_position.qty))
            if qty:
                side = OrderSide.SELL if qty > 0 else OrderSide.BUY
                self._broker.submit_market_order(
                    symbol=hedge_symbol,
                    qty=abs(qty),
                    side=side,
                    time_in_force=self._broker.to_time_in_force(
                        self._broker.strategy.allocation.order_time_in_force
                    ),
                )
