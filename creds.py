"""Utilities for managing Alpaca API credentials.

This module centralises how API keys are loaded so they are not spread
throughout the codebase. Credentials are read from environment variables by
default which keeps them out of version control.
"""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class APICredentials:
    """Alpaca API credentials."""

    api_key: str
    secret_key: str
    paper: bool = True


def load_credentials() -> APICredentials:
    """Load credentials from environment variables.

    Expects ``ALPACA_K`` and ``ALPACA_SK`` to be set for the key ID and secret
    key respectively. ``ALPACA_PAPER`` can be set to ``"false"`` to disable
    paper trading mode.
    """

    try:
        api_key = os.environ["ALPACA_K"]
        secret_key = os.environ["ALPACA_SK"]
    except KeyError as exc:  # pragma: no cover - fail fast during startup
        missing = ", ".join(sorted(name for name in ("ALPACA_K", "ALPACA_SK") if name not in os.environ))
        raise RuntimeError(f"Missing required environment variable(s): {missing}") from exc

    paper = os.environ.get("ALPACA_PAPER", "true").lower() != "false"
    return APICredentials(api_key=api_key, secret_key=secret_key, paper=paper)
