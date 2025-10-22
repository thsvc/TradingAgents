"""Hyperliquid execution stub (structure only, no live IO)."""
from __future__ import annotations

import os
from typing import Dict, List

from tradingagents.execution.base import ExecutionService, OrderResult, OrderStatus, Position, TradePlan


class HyperliquidExecutionService(ExecutionService):
    """Placeholder adapter outlining the required interface."""

    def __init__(self) -> None:
        self.api_key = os.getenv("HYPERLIQUID_API_KEY")
        self.api_secret = os.getenv("HYPERLIQUID_API_SECRET")
        self.account_id = os.getenv("HYPERLIQUID_ACCOUNT_ID")

    def place(self, plan: TradePlan) -> OrderResult:  # pragma: no cover - stub
        raise NotImplementedError("Hyperliquid live execution not implemented")

    def cancel(self, order_id: str) -> bool:  # pragma: no cover - stub
        raise NotImplementedError

    def positions(self) -> List[Position]:  # pragma: no cover - stub
        raise NotImplementedError

    def balances(self) -> Dict[str, float]:  # pragma: no cover - stub
        raise NotImplementedError


__all__ = ["HyperliquidExecutionService"]
