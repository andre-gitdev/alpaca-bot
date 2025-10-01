"""Indicator management for the EMA/SMA crossover strategy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from talipp.indicators import ATR, EMA, SMA


@dataclass(slots=True)
class IndicatorSet:
    """Holds indicator instances and provides update helpers."""

    ema: EMA
    sma: SMA
    atr: ATR

    @classmethod
    def from_config(cls, *, ema_period: int, sma_period: int, atr_period: int) -> "IndicatorSet":
        return cls(EMA(ema_period), SMA(sma_period), ATR(atr_period))

    def seed_from_bars(self, bars: Iterable):
        for bar in bars:
            price = getattr(bar, "close", None)
            if price is None:
                continue
            self.ema.add_input_value(price)
            self.sma.add_input_value(price)
            self.atr.add_input_value(bar)

    def update_from_bar(self, bar) -> None:
        self.ema.add_input_value(bar.close)
        self.sma.add_input_value(bar.close)
        self.atr.add_input_value(bar)

    @property
    def latest_ema(self) -> float | None:
        return self.ema[-1] if len(self.ema) else None

    @property
    def latest_sma(self) -> float | None:
        return self.sma[-1] if len(self.sma) else None
