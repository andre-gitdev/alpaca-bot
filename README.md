# alpaca-bot

This repository contains a Deepnote-authored Jupyter notebook that implements a live trading bot for the SOXL ETF using Alpaca's REST and streaming APIs. The notebook seeds EMA(10) and SMA(50) indicators with early-morning REST bar data, subscribes to minute bars via `StockDataStream`, and routes each update through an asynchronous `handle_trade` routine. There the indicators are refreshed and the bot delegates to `execute_trade_logic`, which decides between holding SOXL or its inverse SOXS based on EMA/SMA crossovers.

The trading logic liquidates opposing positions when signals flip, waits for buying power to reset, and then deploys roughly 90% of available cash on the bullish or bearish leg. Supporting coroutines—such as `clear_all_positions` to flatten exposure near the close—and the `main` entry point orchestrate the websocket event loop with `asyncio.run`. The notebook's dependencies span Alpaca SDKs, technical indicator libraries (`talipp`, `ta`), and plotting/GUI packages like `bokeh`, `mplfinance`, and `PyQt5` to accommodate both trading automation and visualization needs.

## Modular Python scripts

Alongside the notebook, the repository now includes a lightweight module that mirrors the notebook's functionality while exposing reusable components:

- `config.py` centralizes credentials and strategy knobs (tickers, indicator periods, allocation rules).
- `broker.py` wraps Alpaca's REST and streaming clients so strategies can work against a minimal trading interface.
- `indicators.py` houses an `IndicatorSet` helper to seed and update EMA/SMA/ATR state.
- `risk.py` collects reusable routines for buying-power polling and position flattening.
- `strategy.py` ports the EMA/SMA crossover rules into an importable class with an `on_bar` hook.
- `runner.py` wires the pieces together, seeds indicators with historical data, and starts the websocket stream.

For an interactive walkthrough, open `modular_strategy_demo.ipynb`. The first
cell applies `nest_asyncio` so the notebook can reuse its existing Jupyter
event loop when invoking the asynchronous runner—no extra notebook setup
required.

## Bootstrapping dependencies

Before executing the demos or runner, execute the bootstrap helper once to
install any missing requirements:

```
python -m bootstrap
```

Both `runner.py` and `example_simulation.py` call the same helper on startup, so
invoking them directly will install listed dependencies automatically when they
are absent. Set ``auto_install=False`` when calling ``ensure_requirements`` if
you prefer to manage installations manually.

Importing these scripts lets you adjust tickers or trading criteria through configuration rather than editing notebook cells, paving the way for packaging the bot like other open-source trading projects.
