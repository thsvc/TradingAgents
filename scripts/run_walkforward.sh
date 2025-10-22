#!/usr/bin/env bash
set -euo pipefail
export BYPASS_CACHE=1
mkdir -p logs/wf
SEED="${SEED:-123}"
UNIVERSE="${UNIVERSE:-BTC-USD,ETH-USD}"
WINDOWS=(
  "2023-01-01,2023-03-31"
  "2023-04-01,2023-06-30"
  "2023-07-01,2023-09-30"
  "2023-10-01,2023-12-31"
  "2024-01-01,2024-03-31"
  "2024-04-01,2024-06-30"
  "2024-07-01,2024-09-30"
  "2024-10-01,2024-12-31"
  "2025-01-01,2025-03-31"
  "2025-04-01,2025-06-30"
  "2025-07-01,2025-09-30"
)
: > logs/wf/SUMMARY.tsv
echo -e "window\tpoints\tsharpe\tmdd\tlog" >> logs/wf/SUMMARY.tsv
: > logs/wf/METADATA.tsv
echo -e "window\tseed\tstart\tend\tuniverse\tlog" >> logs/wf/METADATA.tsv

for W in "${WINDOWS[@]}"; do
  IFS=, read START END <<< "$W"
  START="$START" END="$END" SEED="$SEED" UNIVERSE="$UNIVERSE" bash scripts/run_baseline.sh
  LATEST=$(cat logs/LATEST)
  OUT="logs/wf/${START}_${END}.jsonl"
  mv "$LATEST" "$OUT" || cp "$LATEST" "$OUT"
  MET=$(python scripts/scorecard.py "$OUT")
  PTS=$(python -c 'import json,sys; j=json.loads(sys.argv[1]); print(j.get("points",0))' "$MET")
  SHR=$(python -c 'import json,sys; j=json.loads(sys.argv[1]); print(j.get("sharpe",0.0))' "$MET")
  MDD=$(python -c 'import json,sys; j=json.loads(sys.argv[1]); print(j.get("mdd",0.0))' "$MET")
  echo -e "${START}→${END}\t${PTS}\t${SHR}\t${MDD}\t${OUT}" >> logs/wf/SUMMARY.tsv
  CONFIG_LINE=$(python - "$OUT" "${START}→${END}" "$SEED" <<'PY'
import json
import sys

path, window, seed = sys.argv[1:4]
with open(path) as fh:
    for line in fh:
        evt = json.loads(line)
        if evt.get("event") == "config":
            print("\t".join([
                window,
                seed,
                str(evt.get("start")),
                str(evt.get("end")),
                str(evt.get("universe")),
                path,
            ]))
            break
    else:
        raise SystemExit(f"No config event found in {path}")
PY
)
  echo "$CONFIG_LINE" >> logs/wf/METADATA.tsv
  echo "$OUT" > logs/LATEST
done
