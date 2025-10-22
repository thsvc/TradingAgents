"""Safety utilities for execution adapters."""
from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict

try:  # Optional dependency for API server helpers
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError:  # pragma: no cover - FastAPI not installed
    FastAPI = None  # type: ignore
    BaseModel = object  # type: ignore


KILLSWITCH_PATH = Path(os.getenv("EXEC_KILLSWITCH_PATH", ".runtime/killswitch.flag"))


def _ensure_runtime_dir() -> None:
    KILLSWITCH_PATH.parent.mkdir(parents=True, exist_ok=True)


def engage_killswitch(state: bool, reason: str | None = None) -> None:
    """Toggle the killswitch flag."""

    _ensure_runtime_dir()
    if state:
        payload = "1" if reason is None else f"1|{reason}"
        KILLSWITCH_PATH.write_text(payload)
    else:
        if KILLSWITCH_PATH.exists():
            KILLSWITCH_PATH.unlink()


def killswitch_engaged() -> bool:
    if not KILLSWITCH_PATH.exists():
        return False
    content = KILLSWITCH_PATH.read_text().strip()
    return content.startswith("1")


def killswitch_reason() -> str | None:
    if not KILLSWITCH_PATH.exists():
        return None
    content = KILLSWITCH_PATH.read_text().strip()
    if "|" in content:
        return content.split("|", 1)[1]
    return None


class BudgetManager:
    """Tracks per-strategy daily budget consumption."""

    def __init__(
        self,
        caps: Dict[str, float],
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._caps = caps
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._day = None
        self._usage: Dict[str, float] = defaultdict(float)

    def _rollover(self) -> None:
        today = self._clock().date()
        if self._day != today:
            self._day = today
            self._usage = defaultdict(float)

    def consume(self, strategy_id: str, notional: float) -> bool:
        self._rollover()
        cap = self._caps.get(strategy_id, self._caps.get("__default__", float("inf")))
        if cap is None or cap == float("inf"):
            self._usage[strategy_id] += notional
            return True
        new_value = self._usage[strategy_id] + notional
        if new_value > cap:
            return False
        self._usage[strategy_id] = new_value
        return True


def parse_budget_caps_from_env(prefix: str = "EXEC_BUDGET_") -> Dict[str, float]:
    caps: Dict[str, float] = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            strategy = key[len(prefix) :].lower()
            try:
                caps[strategy] = float(value)
            except ValueError:
                continue
    if "__default__" not in caps:
        default_cap = os.getenv("EXEC_BUDGET__DEFAULT")
        if default_cap:
            try:
                caps["__default__"] = float(default_cap)
            except ValueError:
                pass
    return caps


if FastAPI is not None:  # pragma: no cover - exercised in manual runs

    class KillSwitchRequest(BaseModel):
        state: bool
        reason: str | None = None

    def create_killswitch_app() -> FastAPI:
        app = FastAPI(title="TradingAgents Kill Switch")

        @app.get("/killswitch")
        def get_state() -> Dict[str, object]:
            return {"engaged": killswitch_engaged(), "reason": killswitch_reason()}

        @app.post("/killswitch")
        def set_state(payload: KillSwitchRequest) -> Dict[str, object]:
            engage_killswitch(payload.state, payload.reason)
            return {"engaged": killswitch_engaged(), "reason": killswitch_reason()}

        return app

else:

    def create_killswitch_app():  # type: ignore[override]
        raise RuntimeError("FastAPI not available; install fastapi to use killswitch API")


__all__ = [
    "BudgetManager",
    "create_killswitch_app",
    "engage_killswitch",
    "killswitch_engaged",
    "killswitch_reason",
    "parse_budget_caps_from_env",
]
