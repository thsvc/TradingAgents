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

Walk-forward (SEED=123, UNIVERSE=BTC-USD,ETH-USD)

| Window | Points | Sharpe | MDD | Log |
|---|---:|---:|---:|---|
| 2023-01-01→2023-03-31 | 66 | -3.181 | 0.158 | `logs/wf/2023-01-01_2023-03-31.jsonl` |
| 2023-04-01→2023-06-30 | 66 | -3.181 | 0.158 | `logs/wf/2023-04-01_2023-06-30.jsonl` |
| 2023-07-01→2023-09-30 | 66 | -3.181 | 0.158 | `logs/wf/2023-07-01_2023-09-30.jsonl` |
| 2023-10-01→2023-12-31 | 66 | -3.181 | 0.158 | `logs/wf/2023-10-01_2023-12-31.jsonl` |
| 2024-01-01→2024-03-31 | 66 | -3.181 | 0.158 | `logs/wf/2024-01-01_2024-03-31.jsonl` |
| 2024-04-01→2024-06-30 | 66 | -3.181 | 0.158 | `logs/wf/2024-04-01_2024-06-30.jsonl` |
| 2024-07-01→2024-09-30 | 67 | -3.109 | 0.158 | `logs/wf/2024-07-01_2024-09-30.jsonl` |
| 2024-10-01→2024-12-31 | 67 | -3.109 | 0.158 | `logs/wf/2024-10-01_2024-12-31.jsonl` |
| 2025-01-01→2025-03-31 | 65 | -3.922 | 0.158 | `logs/wf/2025-01-01_2025-03-31.jsonl` |
| 2025-04-01→2025-06-30 | 66 | -3.181 | 0.158 | `logs/wf/2025-04-01_2025-06-30.jsonl` |
| 2025-07-01→2025-09-30 | 67 | -3.109 | 0.158 | `logs/wf/2025-07-01_2025-09-30.jsonl` |

**Verdict (heuristic):** UNSTABLE
- Sharpe > 0 in 0/11 windows
- Median Sharpe: -3.181
- Median MDD: 0.158
