import json
import os
import tempfile
from pathlib import Path

import pytest

from tradingagents.execution.base import OrderStatus, Side, TradePlan
from tradingagents.execution.paper import PaperExecutionService, PaperConfig
from tradingagents.execution import safety


def make_service(tmp_path: Path, **overrides):
    config = PaperConfig.from_env()
    config = PaperConfig(
        seed=overrides.get("seed", config.seed),
        fee_bps=overrides.get("fee_bps", config.fee_bps),
        journal_path=tmp_path / "journal.jsonl",
        default_spread=overrides.get("default_spread", config.default_spread),
        budget_caps=overrides.get("budget_caps", {"__default__": 1_000_000.0}),
    )
    return PaperExecutionService(config)


def test_paper_execution_records_fill(tmp_path, monkeypatch):
    monkeypatch.setenv("EXEC_BUDGET__DEFAULT", "1000000")
    service = make_service(tmp_path)
    plan = TradePlan(symbol="BTC-USD", side=Side.BUY, quantity=1.0, limit_price=100.0, strategy_id="test")
    result = service.place(plan)
    assert result.status is OrderStatus.FILLED
    journal = (tmp_path / "journal.jsonl").read_text().strip().splitlines()
    assert journal, "journal should contain at least one entry"
    record = json.loads(journal[0])
    assert record["event"] == "order_filled"
    assert record["plan"]["symbol"] == "BTC-USD"


def test_budget_guard_rejects(tmp_path, monkeypatch):
    monkeypatch.setenv("EXEC_BUDGET__DEFAULT", "50")
    service = make_service(tmp_path, budget_caps={"__default__": 50.0})
    plan = TradePlan(symbol="BTC-USD", side=Side.BUY, quantity=1.0, limit_price=100.0, strategy_id="budget")
    result = service.place(plan)
    assert result.status is OrderStatus.REJECTED
    journal = (tmp_path / "journal.jsonl").read_text().strip().splitlines()
    assert json.loads(journal[0])["event"] == "risk_reject"


def test_killswitch_blocks(monkeypatch, tmp_path):
    killswitch_file = tmp_path / "ks.flag"
    monkeypatch.setenv("EXEC_KILLSWITCH_PATH", str(killswitch_file))
    safety.engage_killswitch(True, "test")
    monkeypatch.setenv("EXEC_BUDGET__DEFAULT", "1000000")
    service = make_service(tmp_path)
    plan = TradePlan(symbol="ETH-USD", side=Side.SELL, quantity=0.5, limit_price=200.0, strategy_id="kill")
    result = service.place(plan)
    assert result.status is OrderStatus.REJECTED
    safety.engage_killswitch(False)


def test_baseline_integration_with_paper(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTION_MODE", "paper")
    monkeypatch.setenv("PAPER_JOURNAL_PATH", str(tmp_path / "paper.jsonl"))
    monkeypatch.setenv("EXEC_BUDGET__DEFAULT", "1000000")
    monkeypatch.setenv("PAPER_SEED", "7")
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    import cli.baseline as baseline_module
    import sys

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cli.baseline",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-10",
            "--seed",
            "7",
        ],
    )
    baseline_module.main()
    journal_path = tmp_path / "paper.jsonl"
    assert journal_path.exists()
    lines = journal_path.read_text().strip().splitlines()
    assert any(json.loads(line)["event"] == "order_filled" for line in lines)
