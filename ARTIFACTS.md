Module detected: cli.baseline
Command used: python -m cli.baseline --universe BTC-USD,ETH-USD --start 2024-01-01 --end 2024-06-30 --seed 42 --paper
Scorecard JSON: {"points": 131, "sharpe": -1.132, "mdd": 0.157}
Latest log: logs/baseline_2025-10-22_110243.jsonl
Last 10 log lines:
```jsonl
{"event":"portfolio_mark_to_market","timestamp":"2024-06-18","universe":"BTC-USD,ETH-USD","equity":92778.2}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-19","universe":"BTC-USD,ETH-USD","equity":91629.78}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-20","universe":"BTC-USD,ETH-USD","equity":90330.94}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-21","universe":"BTC-USD,ETH-USD","equity":89800.47}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-24","universe":"BTC-USD,ETH-USD","equity":88674.43}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-25","universe":"BTC-USD,ETH-USD","equity":87898.92}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-26","universe":"BTC-USD,ETH-USD","equity":88775.8}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-27","universe":"BTC-USD,ETH-USD","equity":88818.82}
{"event":"portfolio_mark_to_market","timestamp":"2024-06-28","universe":"BTC-USD,ETH-USD","equity":89128.17}
{"event":"portfolio_equity","timestamp":"2024-06-28","universe":"BTC-USD,ETH-USD","equity":89128.17}
```
Determinism test: pass
Risk-gate test: pass

Walk-forward (SEED=123, UNIVERSE=BTC-USD,ETH-USD, BYPASS_CACHE=1)

| Window | Points | Sharpe | MDD | Log |
|---|---:|---:|---:|---|
| 2023-01-01→2023-03-31 | 66 | 0.276 | 0.051 | `logs/wf/2023-01-01_2023-03-31.jsonl` |
| 2023-04-01→2023-06-30 | 66 | -2.049 | 0.107 | `logs/wf/2023-04-01_2023-06-30.jsonl` |
| 2023-07-01→2023-09-30 | 66 | 1.085 | 0.066 | `logs/wf/2023-07-01_2023-09-30.jsonl` |
| 2023-10-01→2023-12-31 | 66 | 3.884 | 0.040 | `logs/wf/2023-10-01_2023-12-31.jsonl` |
| 2024-01-01→2024-03-31 | 66 | -2.512 | 0.179 | `logs/wf/2024-01-01_2024-03-31.jsonl` |
| 2024-04-01→2024-06-30 | 66 | -1.513 | 0.095 | `logs/wf/2024-04-01_2024-06-30.jsonl` |
| 2024-07-01→2024-09-30 | 67 | 2.374 | 0.035 | `logs/wf/2024-07-01_2024-09-30.jsonl` |
| 2024-10-01→2024-12-31 | 67 | 0.120 | 0.078 | `logs/wf/2024-10-01_2024-12-31.jsonl` |
| 2025-01-01→2025-03-31 | 65 | 2.525 | 0.064 | `logs/wf/2025-01-01_2025-03-31.jsonl` |
| 2025-04-01→2025-06-30 | 66 | -2.640 | 0.143 | `logs/wf/2025-04-01_2025-06-30.jsonl` |
| 2025-07-01→2025-09-30 | 67 | 3.951 | 0.044 | `logs/wf/2025-07-01_2025-09-30.jsonl` |

**Verdict (heuristic):** STABLE-ish
- Sharpe > 0 in 7/11 windows
- Median Sharpe: 0.276
- Median MDD: 0.066
- Config samples:
```tsv
2023-01-01→2023-03-31	123	2023-01-01	2023-03-31	BTC-USD,ETH-USD	logs/wf/2023-01-01_2023-03-31.jsonl
2023-04-01→2023-06-30	123	2023-04-01	2023-06-30	BTC-USD,ETH-USD	logs/wf/2023-04-01_2023-06-30.jsonl
2023-07-01→2023-09-30	123	2023-07-01	2023-09-30	BTC-USD,ETH-USD	logs/wf/2023-07-01_2023-09-30.jsonl
```
