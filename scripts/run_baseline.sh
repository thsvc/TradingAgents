#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
mkdir -p logs
# Find entrypoint module automatically:
ENTRY=$(rg -n "if __name__ == .__main__." -g '!venv' -g '!**/.venv' -S || true)
# Fallback known candidates:
CANDIDATES=("cli.baseline" "tradingagents.run" "run" "main" "app" "trading_agents.run")
MODULE=""
if echo "$ENTRY" | awk -F: '{print $1}' | grep -q '^cli/baseline\.py$'; then
  MODULE="cli.baseline"
else
  MATCH=$(echo "$ENTRY" | awk -F: '{print $1}' | grep -E '\.py$' | grep -v '^scripts/scorecard\.py$' | head -n1 || true)
  if [ -n "$MATCH" ]; then
    PYFILE="$MATCH"
    MODULE=$(echo "$PYFILE" | sed 's/\.py$//' | tr '/' '.')
  fi
fi
if [ -z "$MODULE" ]; then
  for c in "${CANDIDATES[@]}"; do
    if python -c "import ${c}" >/dev/null 2>&1; then
      MODULE="$c"
      break
    fi
  done
fi
if [ -z "$MODULE" ]; then
  echo "❌ Could not auto-detect entrypoint module. Please search README or provide the right module."
  rg -n "python -m" README* || true
  exit 1
fi
START=${START:-"2024-01-01"}
END=${END:-"2024-06-30"}
SEED=${SEED:-"42"}
UNIVERSE=${UNIVERSE:-"BTC-USD,ETH-USD"}
LOG="logs/baseline_$(date +%F_%H%M%S).jsonl"
echo "▶ Running baseline on module: $MODULE"
python -m "$MODULE" --universe "$UNIVERSE" --start "$START" --end "$END" --seed "$SEED" --paper | tee "$LOG"
echo "$LOG" > logs/LATEST
