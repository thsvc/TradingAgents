"""Policy helpers for volatility-aware sizing and trade gating."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class PolicyParams:
    k: float = 0.1
    max_notional: float = 250_000.0
    min_vol: float = 0.5
    max_spread_ratio: float = 0.6
    eps: float = 1e-6


def position_size(atr_14: float, equity: float, params: PolicyParams) -> float:
    atr = max(atr_14, params.eps)
    raw = params.k * equity / atr
    return min(raw, params.max_notional)


def should_trade(atr_14: float, spread: float, params: PolicyParams) -> Tuple[bool, str]:
    if atr_14 < params.min_vol:
        return False, "low_vol"
    atr = max(atr_14, params.eps)
    if spread / atr > params.max_spread_ratio:
        return False, "wide_spread"
    return True, ""


__all__ = ["PolicyParams", "position_size", "should_trade"]
