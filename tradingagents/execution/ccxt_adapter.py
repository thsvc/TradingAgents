"""CCXT execution stub (structure only, no live IO)."""
from __future__ import annotations

import os
from typing import Dict, List

from tradingagents.execution.base import ExecutionService, OrderResult, OrderStatus, Position, TradePlan


class CCXTExecutionService(ExecutionService):
    """Placeholder adapter for CCXT exchanges."""

    def __init__(self) -> None:
        self.exchange_id = os.getenv("CCXT_EXCHANGE", "binance")
        self.api_key = os.getenv("CCXT_API_KEY")
        self.api_secret = os.getenv("CCXT_API_SECRET")
        self.passphrase = os.getenv("CCXT_API_PASSPHRASE")

    def place(self, plan: TradePlan) -> OrderResult:  # pragma: no cover - stub
        raise NotImplementedError("CCXT live execution not implemented")

    def cancel(self, order_id: str) -> bool:  # pragma: no cover - stub
        raise NotImplementedError

    def positions(self) -> List[Position]:  # pragma: no cover - stub
        raise NotImplementedError

    def balances(self) -> Dict[str, float]:  # pragma: no cover - stub
        raise NotImplementedError


__all__ = ["CCXTExecutionService"]
