"""Baseline runner emitting synthetic portfolio marks for smoke tests."""
import argparse
import datetime as dt
import json
import random
from typing import Iterable, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic baseline runner")
    parser.add_argument("--universe", default="BTC-USD,ETH-USD", help="Comma separated tickers")
    parser.add_argument("--start", default="2024-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2024-06-30", help="End date YYYY-MM-DD")
    parser.add_argument("--seed", default="42", help="PRNG seed")
    parser.add_argument("--paper", action="store_true", help="Unused compatibility flag")
    return parser.parse_args()


def iter_trading_days(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    day = start
    while day <= end:
        if day.weekday() < 5:
            yield day
        day += dt.timedelta(days=1)


def simulate_equity_path(days: List[dt.date], seed: str) -> List[float]:
    rng = random.Random(str(seed))
    equity = 100000.0
    path = []
    for _ in days:
        drift = 0.0005
        shock = rng.gauss(0, 0.01)
        change = drift + shock
        equity *= max(0.9, 1.0 + change)
        path.append(round(equity, 2))
    return path


def main() -> None:
    args = parse_args()
    start = dt.datetime.strptime(args.start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(args.end, "%Y-%m-%d").date()
    days = list(iter_trading_days(start, end))
    if not days:
        raise SystemExit("No trading days in the supplied range")

    equities = simulate_equity_path(days, args.seed)

    for day, equity in zip(days, equities):
        payload = {
            "event": "portfolio_mark_to_market",
            "timestamp": day.isoformat(),
            "universe": args.universe,
            "equity": equity,
        }
        print(json.dumps(payload, separators=(",", ":")))

    final_payload = {
        "event": "portfolio_equity",
        "timestamp": days[-1].isoformat(),
        "universe": args.universe,
        "equity": equities[-1],
    }
    print(json.dumps(final_payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
