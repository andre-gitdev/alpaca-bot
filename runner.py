"""Application entry-point that wires configuration, broker, and strategy."""
from __future__ import annotations

import asyncio

from bootstrap import ensure_requirements

# Ensure dependencies are installed before we touch Alpaca SDK modules
ensure_requirements()

from alpaca.data.models import Bar

from broker import AlpacaBroker
from config import AppConfig
from indicators import IndicatorSet
from risk import RiskManager
from strategy import EmaSmaStrategy


def build_app(config: AppConfig) -> tuple[AlpacaBroker, EmaSmaStrategy]:
    broker = AlpacaBroker(config.credentials, config.strategy)
    indicators = IndicatorSet.from_config(
        ema_period=config.strategy.indicators.ema_period,
        sma_period=config.strategy.indicators.sma_period,
        atr_period=config.strategy.indicators.atr_period,
    )
    risk = RiskManager(broker, config.strategy.risk)
    strategy = EmaSmaStrategy(broker, indicators, risk)

    seed_symbol = config.strategy.bullish_symbol
    seed_bars = broker.get_seed_bars(seed_symbol, config.strategy.indicators.seed_bars)
    indicators.seed_from_bars(seed_bars)

    async def handle_bar(bar: Bar):
        await strategy.on_bar(bar)

    symbols = config.strategy.stream.symbols or [seed_symbol]
    broker.subscribe_bars(handle_bar, *symbols)

    return broker, strategy


async def run(config: AppConfig) -> None:
    broker, _ = build_app(config)
    await broker.run_stream()


def main() -> None:
    config = AppConfig.from_env()
    asyncio.run(run(config))


if __name__ == "__main__":
    main()
