"""Ablation runner comparing LLM baseline vs heuristic strategy."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from typing import Iterable, List, Optional, Tuple

from cli import baseline as baseline_cli
from tradingagents import policy, risk
from tradingagents.execution.base import ExecutionService, OrderStatus, Side, TradePlan
from tradingagents.execution.paper import PaperExecutionService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ablation runner over identical windows")
    parser.add_argument("--universe", default="BTC-USD,ETH-USD", help="Comma separated tickers")
    parser.add_argument("--start", default="2024-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2024-06-30", help="End date YYYY-MM-DD")
    parser.add_argument("--seed", default="42", help="PRNG seed")
    parser.add_argument("--mode", choices=("llm", "heur"), default="llm", help="Execution mode")
    parser.add_argument("--paper", action="store_true", help="Unused compatibility flag")
    return parser.parse_args()


def iter_trading_days(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    yield from baseline_cli.iter_trading_days(start, end)


def _load_execution_service() -> Optional[ExecutionService]:
    mode = os.getenv("EXECUTION_MODE", "none").lower()
    if mode in {"none", "noop", "off"}:
        return None
    if mode == "paper":
        return PaperExecutionService.from_env()
    raise SystemExit(f"Unknown EXECUTION_MODE={mode}")


def simulate_heuristic_equity(
    days: List[dt.date],
    seed: str,
    start: dt.date,
    end: dt.date,
    universe: str,
    exec_service: Optional[ExecutionService] = None,
) -> Tuple[List[float], List[int]]:
    prices = baseline_cli.simulate_price_path(days, seed, start, end, universe)
    positions: List[int] = []
    equities: List[float] = []
    equity = 100000.0
    prev_price = prices[0]

    policy_params = policy.PolicyParams()
    risk_params = risk.RiskParams(
        max_daily_loss=5_000.0,
        max_exposure=200_000.0,
        max_concentration_per_symbol=150_000.0,
        cooldown_bars=2,
        min_stop_distance_factor=0.5,
    )
    state = risk.RiskState()
    strategy_id = os.getenv("STRATEGY_ID", "heuristic")
    symbol = universe.split(",")[0]

    for idx, price in enumerate(prices):
        atr = baseline_cli.rolling_atr(prices, idx)
        spread = price * 0.0008
        have_fast, ma_fast = baseline_cli.moving_average(prices, idx, window=10) if hasattr(baseline_cli, "moving_average") else (False, 0.0)
        have_slow, ma_slow = baseline_cli.moving_average(prices, idx, window=50) if hasattr(baseline_cli, "moving_average") else (False, 0.0)

        # Fallback moving average implementation if baseline doesn't expose helper
        if not hasattr(baseline_cli, "moving_average"):
            have_fast, ma_fast = _moving_average(prices, idx, 10)
            have_slow, ma_slow = _moving_average(prices, idx, 50)

        signal = 0
        if have_fast and have_slow:
            if ma_fast > ma_slow * 1.001:
                signal = 1
            elif ma_fast < ma_slow * 0.999:
                signal = -1

        allow, policy_reason = policy.should_trade(atr, spread, policy_params)
        direction = signal if allow else 0
        size = 0.0
        state.decay_cooldown()

        if direction != 0:
            size = policy.position_size(max(atr, policy_params.eps), equity, policy_params)
            try:
                risk.check_trade(size, symbol, max(atr, policy_params.eps), max(atr * 0.5, 1e-6), risk_params, state)
                risk.record_trade(symbol, size, state)
            except risk.RiskRejection as exc:
                direction = 0
                size = 0.0
                print(
                    json.dumps(
                        {
                            "event": "risk_reject",
                            "timestamp": days[idx].isoformat(),
                            "universe": universe,
                            "reason": str(exc),
                            "run_mode": "heur",
                        },
                        separators=(",", ":"),
                    )
                )

        if exec_service and direction != 0:
            quantity = size / max(price, 1e-6)
            plan = TradePlan(
                symbol=symbol,
                side=Side.BUY if direction > 0 else Side.SELL,
                quantity=quantity,
                limit_price=price,
                ttl_seconds=60,
                strategy_id=strategy_id,
                metadata={"mark_price": str(price), "spread": str(spread)},
            )
            result = exec_service.place(plan)
            if result.status is OrderStatus.REJECTED:
                direction = 0
                size = 0.0

        if idx > 0:
            ret = price / prev_price - 1.0
            pnl = direction * size * ret
            equity = max(1_000.0, equity + pnl)
            risk.record_daily_pnl(pnl, risk_params, state)
            risk.release_positions(state, symbol)
        else:
            risk.release_positions(state, symbol)

        equities.append(round(equity, 2))
        positions.append(direction)
        prev_price = price

    return equities, positions


def _moving_average(values: List[float], end_idx: int, window: int) -> Tuple[bool, float]:
    if end_idx + 1 < window:
        return False, 0.0
    window_slice = values[end_idx - window + 1 : end_idx + 1]
    return True, sum(window_slice) / window


def emit_stream(
    days: List[dt.date],
    equities: List[float],
    universe: str,
    run_mode: str,
    positions: Optional[List[int]] = None,
) -> None:
    for idx, (day, equity) in enumerate(zip(days, equities)):
        payload = {
            "event": "portfolio_mark_to_market",
            "timestamp": day.isoformat(),
            "universe": universe,
            "equity": equity,
            "run_mode": run_mode,
        }
        if positions is not None:
            payload["position"] = positions[idx]
        print(json.dumps(payload, separators=(",", ":")))

    final_payload = {
        "event": "portfolio_equity",
        "timestamp": days[-1].isoformat(),
        "universe": universe,
        "equity": equities[-1],
        "run_mode": run_mode,
    }
    if positions is not None:
        final_payload["position"] = positions[-1]
    print(json.dumps(final_payload, separators=(",", ":")))


def main() -> None:
    args = parse_args()
    start = dt.datetime.strptime(args.start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(args.end, "%Y-%m-%d").date()
    days = list(iter_trading_days(start, end))
    if not days:
        raise SystemExit("No trading days in the supplied range")

    print(
        json.dumps(
            {
                "event": "config",
                "start": args.start,
                "end": args.end,
                "universe": args.universe,
                "seed": args.seed,
                "run_mode": args.mode,
                "bypass_cache": os.environ.get("BYPASS_CACHE", "0"),
                "first_trading_day": days[0].isoformat(),
                "last_trading_day": days[-1].isoformat(),
            },
            separators=(",", ":"),
        )
    )

    exec_service = _load_execution_service()

    if args.mode == "llm":
        prices = baseline_cli.simulate_price_path(days, args.seed, start, end, args.universe)
        equities: List[float] = []
        equity = 100000.0
        prev_price = prices[0]
        policy_params = policy.PolicyParams()
        risk_params = risk.RiskParams(
            max_daily_loss=5_000.0,
            max_exposure=200_000.0,
            max_concentration_per_symbol=150_000.0,
            cooldown_bars=2,
            min_stop_distance_factor=0.5,
        )
        state = risk.RiskState()
        strategy_id = os.getenv("STRATEGY_ID", "llm")
        symbol = args.universe.split(",")[0]

        for idx, price in enumerate(prices):
            atr = baseline_cli.rolling_atr(prices, idx)
            spread = price * 0.0008
            allow, policy_reason = policy.should_trade(atr, spread, policy_params)
            direction = 0
            size = 0.0
            state.decay_cooldown()

            if allow:
                size = policy.position_size(max(atr, policy_params.eps), equity, policy_params)
                direction = 1 if price >= prev_price else -1
                try:
                    risk.check_trade(size, symbol, max(atr, policy_params.eps), max(atr * 0.5, 1e-6), risk_params, state)
                    risk.record_trade(symbol, size, state)
                except RiskRejection as exc:
                    direction = 0
                    size = 0.0
                    print(
                        json.dumps(
                            {
                                "event": "risk_reject",
                                "timestamp": days[idx].isoformat(),
                                "universe": args.universe,
                                "reason": str(exc),
                                "run_mode": "llm",
                            },
                            separators=(",", ":"),
                        )
                    )

                if exec_service and direction != 0:
                    quantity = size / max(price, 1e-6)
                    plan = TradePlan(
                        symbol=symbol,
                        side=Side.BUY if direction > 0 else Side.SELL,
                        quantity=quantity,
                        limit_price=price,
                        ttl_seconds=60,
                        strategy_id=strategy_id,
                        metadata={"mark_price": str(price), "spread": str(spread)},
                    )
                    result = exec_service.place(plan)
                    if result.status is OrderStatus.REJECTED:
                        direction = 0
                        size = 0.0
            else:
                direction = 0
                size = 0.0

            if idx > 0:
                ret = price / prev_price - 1.0
                pnl = direction * size * ret
                equity = max(1_000.0, equity + pnl)
                risk.record_daily_pnl(pnl, risk_params, state)
                risk.release_positions(state, symbol)
            else:
                risk.release_positions(state, symbol)

            equities.append(round(equity, 2))
            prev_price = price

        emit_stream(days, equities, args.universe, run_mode="llm")
    else:
        equities, positions = simulate_heuristic_equity(
            days,
            args.seed,
            start,
            end,
            args.universe,
            exec_service=exec_service,
        )
        emit_stream(days, equities, args.universe, run_mode="heur", positions=positions)


if __name__ == "__main__":
    main()
