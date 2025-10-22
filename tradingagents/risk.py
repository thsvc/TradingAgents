"""Minimal risk gate helpers for smoke testing risk limits."""

from dataclasses import dataclass


class RiskRejection(Exception):
    """Raised when a hard risk gate rejects a trade."""


@dataclass
class RiskParams:
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
    """Reject trades that exceed daily loss or exposure caps."""

    if daily_pnl < -abs(max_daily_loss):
        raise RiskRejection("daily loss breached")

    if exposure + abs(position_notional) > max_exposure:
        raise RiskRejection("exposure cap")


__all__ = ["RiskRejection", "hard_risk_gate", "RiskParams"]
