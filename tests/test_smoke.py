import json
import os
import subprocess


def test_smoke_baseline():
    assert os.path.exists("scripts/run_baseline.sh")
    subprocess.check_call(["bash", "scripts/run_baseline.sh"])
    latest = open("logs/LATEST").read().strip()
    assert os.path.exists(latest)
    out = subprocess.check_output(["python", "scripts/scorecard.py", latest]).decode().strip()
    j = json.loads(out)
    assert "sharpe" in j and "mdd" in j and j["points"] > 0
