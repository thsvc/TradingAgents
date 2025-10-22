"""Baseline runner emitting synthetic portfolio marks for smoke tests."""
import argparse
import datetime as dt
import json
import os
import random
from typing import Iterable, List, Tuple

from tradingagents import policy, risk

import hashlib


_CACHE: dict[Tuple[str, str, str, str], List[float]] = {}


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


def _cache_key(start: dt.date, end: dt.date, universe: str, seed: str) -> Tuple[str, str, str, str]:
    return (start.isoformat(), end.isoformat(), universe, str(seed))


def _seed_material(start: dt.date, end: dt.date, universe: str, seed: str) -> str:
    payload = f"{seed}|{start.isoformat()}|{end.isoformat()}|{universe}"
    return hashlib.sha256(payload.encode()).hexdigest()


def simulate_price_path(
    days: List[dt.date], seed: str, start: dt.date, end: dt.date, universe: str
) -> List[float]:
    bypass_cache = os.environ.get("BYPASS_CACHE") in {"1", "true", "TRUE"}
    key = _cache_key(start, end, universe, seed)

    if not bypass_cache and key in _CACHE:
        return list(_CACHE[key])

    rng = random.Random(_seed_material(start, end, universe, seed))
    price = 100.0
    path = []
    for _ in days:
        drift = 0.0005
        shock = rng.gauss(0, 0.01)
        change = drift + shock
        price *= max(0.5, 1.0 + change)
        path.append(round(price, 4))
    if not bypass_cache:
        _CACHE[key] = list(path)

    return path


def rolling_atr(prices: List[float], idx: int, period: int = 14) -> float:
    if idx == 0:
        return 0.0
    start = max(0, idx - period + 1)
    window = prices[start : idx + 1]
    if len(window) < 2:
        return 0.0
    trs = [abs(window[i] / window[i - 1] - 1.0) for i in range(1, len(window))]
    if not trs:
        return 0.0
    return sum(trs) / len(trs) * prices[idx]


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
        "bypass_cache": os.environ.get("BYPASS_CACHE", "0"),
        "first_trading_day": days[0].isoformat(),
        "last_trading_day": days[-1].isoformat(),
    }
    print(json.dumps(config_event, separators=(",", ":")))

    prices = simulate_price_path(days, args.seed, start, end, args.universe)

    equity = 100000.0
    equities: List[float] = []
    prev_price = prices[0]
    prev_equity = equity
    policy_params = policy.PolicyParams()
    symbol = args.universe.split(",")[0]
    risk_params = risk.RiskParams(
        max_daily_loss=5_000.0,
        max_exposure=200_000.0,
        max_concentration_per_symbol=150_000.0,
        cooldown_bars=2,
        min_stop_distance_factor=0.5,
    )
    risk_state = risk.RiskState()

    for idx, (day, price) in enumerate(zip(days, prices)):
        atr = rolling_atr(prices, idx)
        spread = price * 0.0008
        allow_trade, policy_reason = policy.should_trade(atr, spread, policy_params)

        direction = 0
        size = 0.0
        stop_distance = max(atr * 0.5, 1e-6)

        risk_state.decay_cooldown()

        if allow_trade:
            size = policy.position_size(max(atr, policy_params.eps), equity, policy_params)
            direction = 1 if price >= prev_price else -1
            try:
                risk.check_trade(size, symbol, max(atr, policy_params.eps), stop_distance, risk_params, risk_state)
                risk.record_trade(symbol, size, risk_state)
            except risk.RiskRejection as exc:
                direction = 0
                size = 0.0
                print(
                    json.dumps(
                        {
                            "event": "risk_reject",
                            "timestamp": day.isoformat(),
                            "universe": args.universe,
                            "reason": str(exc),
                            "run_mode": "llm",
                        },
                        separators=(",", ":"),
                    )
                )
        else:
            direction = 0
            size = 0.0

        if idx > 0:
            ret = price / prev_price - 1.0
            pnl = direction * size * ret
            equity = max(1_000.0, equity + pnl)
            risk.record_daily_pnl(pnl, risk_params, risk_state)
            risk.release_positions(risk_state, symbol)
        else:
            risk.release_positions(risk_state, symbol)

        equities.append(round(equity, 2))

        payload = {
            "event": "portfolio_mark_to_market",
            "timestamp": day.isoformat(),
            "universe": args.universe,
            "equity": equities[-1],
            "price": round(price, 4),
            "atr_14": round(atr, 6),
            "position_notional": round(direction * size, 2),
            "run_mode": "llm",
        }
        if not allow_trade:
            payload["policy_reason"] = policy_reason
        print(json.dumps(payload, separators=(",", ":")))

        prev_price = price
        prev_equity = equity

    final_payload = {
        "event": "portfolio_equity",
        "timestamp": days[-1].isoformat(),
        "universe": args.universe,
        "equity": equities[-1],
        "run_mode": "llm",
    }
    print(json.dumps(final_payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
