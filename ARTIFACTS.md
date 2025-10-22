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
