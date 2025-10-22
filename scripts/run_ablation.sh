#!/usr/bin/env bash
set -euo pipefail
export BYPASS_CACHE=1
mkdir -p logs/ablation
SEED="${SEED:-123}"
UNIVERSE="${UNIVERSE:-BTC-USD,ETH-USD}"
WINDOW_FILE="logs/wf/SUMMARY.tsv"
if [ ! -f "$WINDOW_FILE" ]; then
  echo "Missing window summary: $WINDOW_FILE" >&2
  exit 1
fi
: > logs/ablation/SUMMARY.tsv
echo -e "window\tmode\tpoints\tsharpe\tmdd\tlog" >> logs/ablation/SUMMARY.tsv

while IFS=$'\t' read -r WINDOW POINTS SHARPE MDD LOGPATH; do
  if [ "$WINDOW" = "window" ] || [ -z "$WINDOW" ]; then
    continue
  fi
  IFS=$'→' read -r START END <<< "$WINDOW"
  for MODE in llm heur; do
    OUT="logs/ablation/${START}_${END}_${MODE}.jsonl"
    python -m cli.ablation --mode "$MODE" --start "$START" --end "$END" --seed "$SEED" --universe "$UNIVERSE" > "$OUT"
    MET=$(python scripts/scorecard.py "$OUT")
    PTS=$(python -c 'import json,sys; j=json.loads(sys.argv[1]); print(j.get("points",0))' "$MET")
    SHR=$(python -c 'import json,sys; j=json.loads(sys.argv[1]); print(j.get("sharpe",0.0))' "$MET")
    MDD_VAL=$(python -c 'import json,sys; j=json.loads(sys.argv[1]); print(j.get("mdd",0.0))' "$MET")
    echo -e "${WINDOW}\t${MODE}\t${PTS}\t${SHR}\t${MDD_VAL}\t${OUT}" >> logs/ablation/SUMMARY.tsv
  done
done < "$WINDOW_FILE"

python - "$SEED" "$UNIVERSE" <<'PY' > logs/ablation/SUMMARY.md
import json
import statistics as st
import sys
from pathlib import Path

seed, universe = sys.argv[1:3]
rows = []
with Path("logs/ablation/SUMMARY.tsv").open() as fh:
    next(fh)
    for line in fh:
        window, mode, points, sharpe, mdd, log = line.rstrip().split("\t")
        rows.append((window, mode, int(points), float(sharpe), float(mdd), log))

rows.sort(key=lambda r: (r[0], r[1]))

lines = ["## Ablation Summary", "", "| Window | Mode | Points | Sharpe | MDD | Log |", "|---|---|---:|---:|---:|---|"]
for window, mode, pts, sharpe, mdd, log in rows:
    lines.append(f"| {window} | {mode} | {pts} | {sharpe:.3f} | {mdd:.3f} | `{log}` |")

from collections import defaultdict

by_window = defaultdict(dict)
for window, mode, pts, sharpe, mdd, log in rows:
    by_window[window][mode] = sharpe

deltas = []
win_count = 0
for window, sharpe_map in by_window.items():
    if "llm" in sharpe_map and "heur" in sharpe_map:
        delta = sharpe_map["llm"] - sharpe_map["heur"]
        deltas.append(delta)
        if delta > 0:
            win_count += 1

lines.append("")
if deltas:
    median_delta = st.median(deltas)
    lines.append(f"**Median Sharpe delta (LLM-Heur):** {median_delta:.3f}")
    lines.append(f"- LLM Sharpe > Heur in {win_count}/{len(deltas)} windows")
else:
    lines.append("**Median Sharpe delta (LLM-Heur):** n/a")

print("\n".join(lines))
PY
