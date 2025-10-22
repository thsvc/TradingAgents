"""Ablation runner comparing LLM-inspired baseline against a heuristic trend follower."""
import argparse
import datetime as dt
import json
import os
import random
from typing import Iterable, List, Optional, Tuple

from cli import baseline as baseline_cli


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ablation runner over identical windows")
    parser.add_argument("--universe", default="BTC-USD,ETH-USD", help="Comma separated tickers")
    parser.add_argument("--start", default="2024-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2024-06-30", help="End date YYYY-MM-DD")
    parser.add_argument("--seed", default="42", help="PRNG seed")
    parser.add_argument(
        "--mode",
        choices=("llm", "heur"),
        default="llm",
        help="Run mode: synthetic LLM baseline or heuristic MA cross",
    )
    parser.add_argument("--paper", action="store_true", help="Unused compatibility flag")
    return parser.parse_args()


def iter_trading_days(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    yield from baseline_cli.iter_trading_days(start, end)


def _price_seed(start: dt.date, end: dt.date, universe: str, seed: str) -> str:
    material = baseline_cli._seed_material(start, end, universe, f"price|{seed}")  # type: ignore[attr-defined]
    return material


def simulate_price_path(
    days: List[dt.date], seed: str, start: dt.date, end: dt.date, universe: str
) -> List[float]:
    rng = random.Random(_price_seed(start, end, universe, seed))
    price = 100.0
    path: List[float] = []
    for _ in days:
        drift = 0.0008
        shock = rng.gauss(0, 0.012)
        change = drift + shock
        price *= max(0.1, 1.0 + change)
        path.append(round(price, 4))
    return path


def moving_average(values: List[float], end_idx: int, window: int) -> Tuple[bool, float]:
    if end_idx + 1 < window:
        return False, 0.0
    window_slice = values[end_idx - window + 1 : end_idx + 1]
    return True, sum(window_slice) / window


def simulate_heuristic_equity(
    days: List[dt.date], seed: str, start: dt.date, end: dt.date, universe: str
) -> Tuple[List[float], List[int]]:
    prices = simulate_price_path(days, seed, start, end, universe)
    positions: List[int] = []
    equity = 100000.0
    equities: List[float] = []

    prev_price = prices[0]
    prev_position = 0

    for idx, price in enumerate(prices):
        have_fast, ma_fast = moving_average(prices, idx, 10)
        have_slow, ma_slow = moving_average(prices, idx, 50)

        if have_fast and have_slow:
            if ma_fast > ma_slow * 1.001:
                position = 1
            elif ma_fast < ma_slow * 0.999:
                position = -1
            else:
                position = 0
        else:
            position = 0

        if idx > 0:
            ret = (price / prev_price) - 1.0
            equity *= 1.0 + prev_position * ret

        equities.append(round(equity, 2))
        positions.append(position)

        prev_price = price
        prev_position = position

    return equities, positions


def emit_stream(
    days: List[dt.date],
    equities: List[float],
    universe: str,
    run_mode: str,
    positions: Optional[List[int]] = None,
) -> None:
    for idx, (day, equity) in enumerate(zip(days, equities)):
        payload_extra = {}
        if positions is not None:
            payload_extra["position"] = positions[idx]
        payload = {
            "event": "portfolio_mark_to_market",
            "timestamp": day.isoformat(),
            "universe": universe,
            "equity": equity,
            "run_mode": run_mode,
        }
        payload.update(payload_extra)
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

    config_event = {
        "event": "config",
        "start": args.start,
        "end": args.end,
        "universe": args.universe,
        "seed": args.seed,
        "run_mode": args.mode,
        "bypass_cache": os.environ.get("BYPASS_CACHE", "0"),
        "first_trading_day": days[0].isoformat(),
        "last_trading_day": days[-1].isoformat(),
    }
    print(json.dumps(config_event, separators=(",", ":")))

    if args.mode == "llm":
        equities = baseline_cli.simulate_equity_path(days, args.seed, start, end, args.universe)
        emit_stream(days, equities, args.universe, run_mode="llm")
    else:
        equities, positions = simulate_heuristic_equity(days, args.seed, start, end, args.universe)
        emit_stream(days, equities, args.universe, run_mode="heur", positions=positions)


if __name__ == "__main__":
    main()
