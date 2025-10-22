import json
import os
import subprocess
from pathlib import Path


CMD = ["bash", "scripts/run_baseline.sh"]


def _run_window(start: str, end: str) -> Path:
    env = os.environ.copy()
    env.update(
        {
            "START": start,
            "END": end,
            "SEED": "4242",
            "UNIVERSE": "BTC-USD,ETH-USD",
            "BYPASS_CACHE": "1",
        }
    )
    subprocess.check_call(CMD, env=env)
    latest = Path("logs/LATEST").read_text().strip()
    return Path(latest)


def _load_event(path: Path, name: str) -> dict:
    with path.open() as fh:
        for line in fh:
            payload = json.loads(line)
            if payload.get("event") == name:
                return payload
    raise AssertionError(f"event={name!r} not found in {path}")


def _first_mark_timestamp(path: Path) -> str:
    with path.open() as fh:
        for line in fh:
            payload = json.loads(line)
            if payload.get("event") == "portfolio_mark_to_market":
                return payload["timestamp"]
    raise AssertionError("No portfolio_mark_to_market events found")


def test_timewindow_wiring_differs_between_runs():
    p_q1 = _run_window("2024-01-01", "2024-03-31")
    config_q1 = _load_event(p_q1, "config")
    first_ts_q1 = _first_mark_timestamp(p_q1)

    p_q2 = _run_window("2024-04-01", "2024-06-30")
    config_q2 = _load_event(p_q2, "config")
    first_ts_q2 = _first_mark_timestamp(p_q2)

    assert config_q1["start"] == "2024-01-01"
    assert config_q2["start"] == "2024-04-01"
    assert config_q1["start"] != config_q2["start"]
    assert config_q1["end"] != config_q2["end"]

    assert first_ts_q1 != first_ts_q2, "Expect distinct mark-to-market windows"
