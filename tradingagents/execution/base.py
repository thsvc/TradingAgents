"""Execution service interfaces and shared primitives."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable


class OrderStatus(str, Enum):
    FILLED = "filled"
    REJECTED = "rejected"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class TradePlan:
    symbol: str
    side: Side
    quantity: float
    limit_price: Optional[float] = None
    ttl_seconds: int = 60
    strategy_id: str = "baseline"
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class OrderResult:
    order_id: str
    status: OrderStatus
    filled_qty: float
    average_price: float
    fees_paid: float
    timestamp: float
    raw: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    average_price: float


@runtime_checkable
class ExecutionService(Protocol):
    """Interface expected from execution backends."""

    def place(self, plan: TradePlan) -> OrderResult:
        """Submit a trade plan for execution."""

    def cancel(self, order_id: str) -> bool:
        """Attempt to cancel an order, returning success state."""

    def positions(self) -> List[Position]:
        """Return open positions currently tracked by the adapter."""

    def balances(self) -> Dict[str, float]:
        """Return available balances in quote/base currencies."""


__all__ = [
    "ExecutionService",
    "OrderResult",
    "OrderStatus",
    "Position",
    "Side",
    "TradePlan",
]
