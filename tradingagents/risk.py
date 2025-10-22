"""Risk management helpers for volatility-aware guardrails."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


class RiskRejection(Exception):
    """Raised when a hard risk gate rejects a trade."""


@dataclass
class RiskParams:
    max_daily_loss: float
    max_exposure: float
    max_concentration_per_symbol: float
    cooldown_bars: int = 3
    min_stop_distance_factor: float = 0.5


@dataclass
class RiskState:
    total_exposure: float = 0.0
    symbol_exposure: Dict[str, float] = field(default_factory=dict)
    cooldown_bars_remaining: int = 0

    def reset_exposure(self) -> None:
        self.total_exposure = 0.0
        self.symbol_exposure.clear()

    def decay_cooldown(self) -> None:
        if self.cooldown_bars_remaining > 0:
            self.cooldown_bars_remaining -= 1

    def start_cooldown(self, bars: int) -> None:
        self.cooldown_bars_remaining = max(self.cooldown_bars_remaining, bars)


def check_trade(
    notional: float,
    symbol: str,
    atr_14: float,
    stop_distance: float,
    params: RiskParams,
    state: RiskState,
) -> None:
    """Run pre-trade risk checks; raise RiskRejection on violations."""

    if state.cooldown_bars_remaining > 0:
        raise RiskRejection("cooldown")

    next_total = state.total_exposure + abs(notional)
    if next_total > params.max_exposure:
        raise RiskRejection("exposure cap")

    symbol_total = state.symbol_exposure.get(symbol, 0.0) + abs(notional)
    if symbol_total > params.max_concentration_per_symbol:
        raise RiskRejection("concentration cap")

    if stop_distance < params.min_stop_distance_factor * max(atr_14, 1e-9):
        raise RiskRejection("stop too tight")


def record_trade(symbol: str, notional: float, state: RiskState) -> None:
    state.total_exposure += abs(notional)
    state.symbol_exposure[symbol] = state.symbol_exposure.get(symbol, 0.0) + abs(notional)


def release_positions(state: RiskState, symbol: str | None = None) -> None:
    if symbol is None:
        state.reset_exposure()
    else:
        exposure = state.symbol_exposure.pop(symbol, 0.0)
        state.total_exposure = max(0.0, state.total_exposure - exposure)


def record_daily_pnl(pnl: float, params: RiskParams, state: RiskState) -> None:
    if pnl < -abs(params.max_daily_loss):
        state.start_cooldown(params.cooldown_bars)


# Legacy helper retained for backwards compatibility in earlier tests.
@dataclass
class LegacyParams:
    position_notional: float
    exposure: float
    max_exposure: float
    daily_pnl: float
    max_daily_loss: float


def hard_risk_gate(
    position_notional: float,
    exposure: float,
    max_exposure: float,
    daily_pnl: float,
    max_daily_loss: float,
) -> None:
    if daily_pnl < -abs(max_daily_loss):
        raise RiskRejection("daily loss breached")
    if exposure + abs(position_notional) > max_exposure:
        raise RiskRejection("exposure cap")


__all__ = [
    "RiskRejection",
    "RiskParams",
    "RiskState",
    "check_trade",
    "record_trade",
    "release_positions",
    "record_daily_pnl",
    "hard_risk_gate",
]
