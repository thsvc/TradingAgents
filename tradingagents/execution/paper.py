"""Deterministic paper execution adapter with journaling."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from tradingagents.execution.base import (
    ExecutionService,
    OrderResult,
    OrderStatus,
    Position,
    Side,
    TradePlan,
)
from tradingagents.execution import safety


@dataclass
class PaperConfig:
    seed: int = 42
    fee_bps: float = 5.0
    journal_path: Path = Path("logs/execution/paper_journal.jsonl")
    default_spread: float = 0.5
    budget_caps: Dict[str, float] = None  # type: ignore[assignment]

    @classmethod
    def from_env(cls) -> "PaperConfig":
        seed = int(os.getenv("PAPER_SEED", "42"))
        fee_bps = float(os.getenv("PAPER_FEE_BPS", "5"))
        journal_path = Path(os.getenv("PAPER_JOURNAL_PATH", "logs/execution/paper_journal.jsonl"))
        default_spread = float(os.getenv("PAPER_DEFAULT_SPREAD", "0.5"))
        caps = safety.parse_budget_caps_from_env()
        return cls(seed=seed, fee_bps=fee_bps, journal_path=journal_path, default_spread=default_spread, budget_caps=caps)


class PaperExecutionService(ExecutionService):
    def __init__(self, config: PaperConfig) -> None:
        import random

        self._config = config
        self._rng = random.Random(config.seed)
        self._positions: Dict[str, Position] = {}
        self._balances: Dict[str, float] = {"USD": 1_000_000.0}
        self._journal_path = config.journal_path
        self._journal_path.parent.mkdir(parents=True, exist_ok=True)
        self._budget = safety.BudgetManager(config.budget_caps or {"__default__": 1_000_000.0})

    @classmethod
    def from_env(cls) -> "PaperExecutionService":
        return cls(PaperConfig.from_env())

    # ExecutionService API -------------------------------------------------
    def place(self, plan: TradePlan) -> OrderResult:
        timestamp = time.time()
        reason = None

        if safety.killswitch_engaged():
            reason = safety.killswitch_reason() or "killswitch_engaged"
            return self._reject(plan, timestamp, reason)

        mark_price = _extract_mark_price(plan)
        notional = abs(plan.quantity) * mark_price
        if not self._budget.consume(plan.strategy_id.lower(), notional):
            reason = "budget_exceeded"
            return self._reject(plan, timestamp, reason)

        spread = _extract_spread(plan, self._config.default_spread)
        slip = self._calculate_slippage(spread, plan.quantity)
        fill_price = mark_price + slip if plan.side == Side.BUY else mark_price - slip
        fees = notional * (self._config.fee_bps / 10_000.0)

        self._apply_fill(plan, fill_price, plan.quantity, fees)
        order_id = f"paper-{uuid.uuid4().hex[:12]}"
        result = OrderResult(
            order_id=order_id,
            status=OrderStatus.FILLED,
            filled_qty=plan.quantity,
            average_price=fill_price,
            fees_paid=fees,
            timestamp=timestamp,
            raw={
                "notional": notional,
                "spread": spread,
                "slippage": slip,
            },
        )
        self._journal_event(
            {
                "event": "order_filled",
                "plan": _plan_to_dict(plan),
                "result": _result_to_dict(result),
            }
        )
        return result

    def cancel(self, order_id: str) -> bool:
        self._journal_event({"event": "cancel", "order_id": order_id})
        return False

    def positions(self) -> List[Position]:
        return list(self._positions.values())

    def balances(self) -> Dict[str, float]:
        return dict(self._balances)

    # Internal helpers -----------------------------------------------------
    def _reject(self, plan: TradePlan, timestamp: float, reason: str) -> OrderResult:
        order_id = f"paper-reject-{uuid.uuid4().hex[:12]}"
        result = OrderResult(
            order_id=order_id,
            status=OrderStatus.REJECTED,
            filled_qty=0.0,
            average_price=0.0,
            fees_paid=0.0,
            timestamp=timestamp,
            raw={"reason": reason},
        )
        self._journal_event(
            {
                "event": "risk_reject",
                "reason": reason,
                "plan": _plan_to_dict(plan),
                "result": _result_to_dict(result),
            }
        )
        return result

    def _calculate_slippage(self, spread: float, quantity: float) -> float:
        impact = self._rng.uniform(0.0, spread) * 0.5
        size_factor = abs(quantity) * 1e-4
        return impact + size_factor

    def _apply_fill(self, plan: TradePlan, price: float, quantity: float, fees: float) -> None:
        symbol = plan.symbol
        current = self._positions.get(symbol)
        qty = quantity if plan.side == Side.BUY else -quantity
        notional = price * quantity
        if current:
            new_qty = current.quantity + qty
            if abs(new_qty) < 1e-9:
                del self._positions[symbol]
            else:
                avg_price = (current.average_price * current.quantity + price * qty) / new_qty
                self._positions[symbol] = Position(symbol=symbol, quantity=new_qty, average_price=avg_price)
        else:
            self._positions[symbol] = Position(symbol=symbol, quantity=qty, average_price=price)

        usd = self._balances.get("USD", 0.0)
        delta = notional + fees
        if plan.side == Side.BUY:
            usd -= delta
        else:
            usd += delta
        self._balances["USD"] = usd

    def _journal_event(self, payload: Dict[str, object]) -> None:
        record = json.dumps({"timestamp": time.time(), **payload}, separators=(",", ":"))
        with self._journal_path.open("a") as fh:
            fh.write(record + "\n")


def _plan_to_dict(plan: TradePlan) -> Dict[str, object]:
    return {
        "symbol": plan.symbol,
        "side": plan.side.value,
        "quantity": plan.quantity,
        "limit_price": plan.limit_price,
        "ttl_seconds": plan.ttl_seconds,
        "strategy_id": plan.strategy_id,
        "metadata": plan.metadata,
    }


def _result_to_dict(result: OrderResult) -> Dict[str, object]:
    return {
        "order_id": result.order_id,
        "status": result.status.value,
        "filled_qty": result.filled_qty,
        "average_price": result.average_price,
        "fees_paid": result.fees_paid,
        "timestamp": result.timestamp,
        "raw": result.raw,
    }


def _extract_mark_price(plan: TradePlan) -> float:
    if plan.limit_price:
        return plan.limit_price
    price = plan.metadata.get("mark_price") if isinstance(plan.metadata, dict) else None
    if price is not None:
        try:
            return float(price)
        except (TypeError, ValueError):
            pass
    return 100.0


def _extract_spread(plan: TradePlan, default: float) -> float:
    if isinstance(plan.metadata, dict) and "spread" in plan.metadata:
        try:
            return float(plan.metadata["spread"])
        except (TypeError, ValueError):
            return default
    return default


__all__ = ["PaperExecutionService", "PaperConfig"]
