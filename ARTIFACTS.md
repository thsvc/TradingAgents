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
| 2023-01-01→2023-03-31 | 66 | 19.302 | 0.000 | `logs/wf/2023-01-01_2023-03-31.jsonl` |
| 2023-04-01→2023-06-30 | 66 | 20.520 | 0.000 | `logs/wf/2023-04-01_2023-06-30.jsonl` |
| 2023-07-01→2023-09-30 | 66 | 20.368 | 0.000 | `logs/wf/2023-07-01_2023-09-30.jsonl` |
| 2023-10-01→2023-12-31 | 66 | 19.950 | 0.000 | `logs/wf/2023-10-01_2023-12-31.jsonl` |
| 2024-01-01→2024-03-31 | 66 | 23.819 | 0.000 | `logs/wf/2024-01-01_2024-03-31.jsonl` |
| 2024-04-01→2024-06-30 | 66 | 16.888 | 0.000 | `logs/wf/2024-04-01_2024-06-30.jsonl` |
| 2024-07-01→2024-09-30 | 67 | 22.343 | 0.000 | `logs/wf/2024-07-01_2024-09-30.jsonl` |
| 2024-10-01→2024-12-31 | 67 | 19.822 | 0.000 | `logs/wf/2024-10-01_2024-12-31.jsonl` |
| 2025-01-01→2025-03-31 | 65 | 18.952 | 0.000 | `logs/wf/2025-01-01_2025-03-31.jsonl` |
| 2025-04-01→2025-06-30 | 66 | 22.672 | 0.000 | `logs/wf/2025-04-01_2025-06-30.jsonl` |
| 2025-07-01→2025-09-30 | 67 | 20.975 | 0.000 | `logs/wf/2025-07-01_2025-09-30.jsonl` |

**Verdict (heuristic):** STABLE-ish
- Sharpe > 0 in 11/11 windows
- Median Sharpe: 20.368
- Median MDD: 0.000
- Config samples:
```tsv
2023-01-01→2023-03-31	123	2023-01-01	2023-03-31	BTC-USD,ETH-USD	logs/wf/2023-01-01_2023-03-31.jsonl
2023-04-01→2023-06-30	123	2023-04-01	2023-06-30	BTC-USD,ETH-USD	logs/wf/2023-04-01_2023-06-30.jsonl
2023-07-01→2023-09-30	123	2023-07-01	2023-09-30	BTC-USD,ETH-USD	logs/wf/2023-07-01_2023-09-30.jsonl
```

Ablations (SEED=123, UNIVERSE=BTC-USD,ETH-USD, BYPASS_CACHE=1)

| Window | Mode | Points | Sharpe | MDD | Log |
|---|---|---:|---:|---:|---|
| 2023-01-01→2023-03-31 | heur | 66 | -0.586 | 0.004 | `logs/ablation/2023-01-01_2023-03-31_heur.jsonl` |
| 2023-01-01→2023-03-31 | llm | 66 | 19.302 | 0.000 | `logs/ablation/2023-01-01_2023-03-31_llm.jsonl` |
| 2023-04-01→2023-06-30 | heur | 66 | -3.077 | 0.006 | `logs/ablation/2023-04-01_2023-06-30_heur.jsonl` |
| 2023-04-01→2023-06-30 | llm | 66 | 20.520 | 0.000 | `logs/ablation/2023-04-01_2023-06-30_llm.jsonl` |
| 2023-07-01→2023-09-30 | heur | 66 | -0.027 | 0.003 | `logs/ablation/2023-07-01_2023-09-30_heur.jsonl` |
| 2023-07-01→2023-09-30 | llm | 66 | 20.368 | 0.000 | `logs/ablation/2023-07-01_2023-09-30_llm.jsonl` |
| 2023-10-01→2023-12-31 | heur | 66 | -0.436 | 0.003 | `logs/ablation/2023-10-01_2023-12-31_heur.jsonl` |
| 2023-10-01→2023-12-31 | llm | 66 | 19.950 | 0.000 | `logs/ablation/2023-10-01_2023-12-31_llm.jsonl` |
| 2024-01-01→2024-03-31 | heur | 66 | -2.579 | 0.008 | `logs/ablation/2024-01-01_2024-03-31_heur.jsonl` |
| 2024-01-01→2024-03-31 | llm | 66 | 23.819 | 0.000 | `logs/ablation/2024-01-01_2024-03-31_llm.jsonl` |
| 2024-04-01→2024-06-30 | heur | 66 | 3.647 | 0.001 | `logs/ablation/2024-04-01_2024-06-30_heur.jsonl` |
| 2024-04-01→2024-06-30 | llm | 66 | 16.888 | 0.000 | `logs/ablation/2024-04-01_2024-06-30_llm.jsonl` |
| 2024-07-01→2024-09-30 | heur | 67 | -0.570 | 0.004 | `logs/ablation/2024-07-01_2024-09-30_heur.jsonl` |
| 2024-07-01→2024-09-30 | llm | 67 | 22.343 | 0.000 | `logs/ablation/2024-07-01_2024-09-30_llm.jsonl` |
| 2024-10-01→2024-12-31 | heur | 67 | 2.001 | 0.001 | `logs/ablation/2024-10-01_2024-12-31_heur.jsonl` |
| 2024-10-01→2024-12-31 | llm | 67 | 19.822 | 0.000 | `logs/ablation/2024-10-01_2024-12-31_llm.jsonl` |
| 2025-01-01→2025-03-31 | heur | 65 | -0.636 | 0.004 | `logs/ablation/2025-01-01_2025-03-31_heur.jsonl` |
| 2025-01-01→2025-03-31 | llm | 65 | 18.952 | 0.000 | `logs/ablation/2025-01-01_2025-03-31_llm.jsonl` |
| 2025-04-01→2025-06-30 | heur | 66 | 0.967 | 0.004 | `logs/ablation/2025-04-01_2025-06-30_heur.jsonl` |
| 2025-04-01→2025-06-30 | llm | 66 | 22.672 | 0.000 | `logs/ablation/2025-04-01_2025-06-30_llm.jsonl` |
| 2025-07-01→2025-09-30 | heur | 67 | 4.460 | 0.002 | `logs/ablation/2025-07-01_2025-09-30_heur.jsonl` |
| 2025-07-01→2025-09-30 | llm | 67 | 20.975 | 0.000 | `logs/ablation/2025-07-01_2025-09-30_llm.jsonl` |

**Median Sharpe delta (LLM-Heur):** 20.386
- LLM Sharpe > Heur in 11/11 windows

Policy/Risk v1 (vol-aware sizing + guardrails)

- Verdict: STABLE-ish (Sharpe > 0 in 11/11 windows)
- Median Sharpe: 20.368
- Median MDD: 0.000
- Source: `logs/wf/SUMMARY.md`
