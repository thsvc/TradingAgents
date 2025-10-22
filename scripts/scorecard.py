import json
import sys


def read_equity(path):
    eq = []
    with open(path) as f:
        for line in f:
            try:
                ev = json.loads(line)
                if ev.get("event") in ("portfolio_mark_to_market", "portfolio_equity"):
                    eq.append(float(ev.get("equity", ev.get("value", 0))))
            except Exception:
                pass
    return eq


def sharpe(e):
    if len(e) < 2:
        return 0.0
    rets = [(e[i] / e[i - 1] - 1.0) for i in range(1, len(e))]
    if not rets:
        return 0.0
    mu = sum(rets) / len(rets)
    sd = (sum((r - mu) ** 2 for r in rets) / len(rets)) ** 0.5
    return 0.0 if sd == 0 else (mu / sd) * (252 ** 0.5)


def mdd(e):
    if not e:
        return 0.0
    peak = e[0]
    dd = 0.0
    for x in e:
        peak = max(peak, x)
        dd = max(dd, (peak - x) / peak if peak else 0.0)
    return dd


if __name__ == "__main__":
    path = sys.argv[1]
    eq = read_equity(path)
    out = {
        "points": len(eq),
        "sharpe": round(sharpe(eq), 3),
        "mdd": round(mdd(eq), 3),
    }
    print(json.dumps(out))
