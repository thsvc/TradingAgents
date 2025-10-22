import hashlib
import os
import subprocess
import time

CMD = ["bash", "scripts/run_baseline.sh"]


def _digest(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_runs_are_identical():
    os.environ["SEED"] = "123"
    os.environ["START"] = "2024-01-01"
    os.environ["END"] = "2024-03-31"
    os.environ["UNIVERSE"] = "BTC-USD,ETH-USD"

    subprocess.check_call(CMD)
    p1 = open("logs/LATEST").read().strip()

    time.sleep(1)
    subprocess.check_call(CMD)
    p2 = open("logs/LATEST").read().strip()

    assert os.path.exists(p1)
    assert os.path.exists(p2)

    d1, d2 = _digest(p1), _digest(p2)
    assert d1 == d2, f"Non-determinism detected: {p1} ({d1}) vs {p2} ({d2})"
