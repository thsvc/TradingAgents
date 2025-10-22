# Execution Adapters

This repository ships a layered execution stack that lets you dry-run strategies locally and plug in live adapters when you're ready.

## Components

| Module | Purpose |
| --- | --- |
| `tradingagents.execution.base` | Shared protocol (`ExecutionService`) + dataclasses (`TradePlan`, `OrderResult`). |
| `tradingagents.execution.paper` | Deterministic paper engine with slippage, fees, budgets, and JSONL journaling. |
| `tradingagents.execution.hyperliquid` | Stub outlining how a Hyperliquid adapter would be structured (keys loaded from env). |
| `tradingagents.execution.ccxt_adapter` | Stub for CCXT-style venues (exchange id, key/secret). |
| `tradingagents.execution.safety` | Killswitch helpers + per-strategy budget manager + FastAPI toggle endpoint. |

## Paper Execution

```bash
# .env (or export) – example defaults
EXECUTION_MODE=paper
PAPER_JOURNAL_PATH=logs/execution/paper_journal.jsonl
PAPER_SEED=123
PAPER_DEFAULT_SPREAD=0.5
PAPER_FEE_BPS=5
EXEC_BUDGET__DEFAULT=500000
```

Run the baseline:

```bash
python -m cli.baseline --start 2024-01-01 --end 2024-02-01 --seed 123
```

Inspect fills:

```bash
jq '.' logs/execution/paper_journal.jsonl | head
```

## Live Stubs

Both Hyperliquid and CCXT adapters expose the same `ExecutionService` surface but intentionally raise `NotImplementedError`. Wire your preferred SDK in `place`, `cancel`, etc., sourcing credentials from env vars (see `.env.example`).

## Kill Switch

* File flag: `EXEC_KILLSWITCH_PATH` (defaults to `.runtime/killswitch.flag`).
* API server:

```bash
uvicorn tradingagents.execution.safety:create_killswitch_app --factory --reload
```

*Endpoints*

- `GET /killswitch` → `{ "engaged": bool, "reason": str | null }`
- `POST /killswitch { "state": true, "reason": "maintenance" }`

Any engaged state makes paper/live adapters return `risk_reject`.

## Safety Checklist Before Going Live

1. Set `EXECUTION_MODE=none` by default in all dev shells.
2. Store API keys in GitHub Environments or external secret managers.
3. Configure per-strategy caps (`EXEC_BUDGET_<strategy>=...`).
4. Run through paper trading with the same budgets and verify journals.
5. Confirm kill switch path is writable and monitored.
6. Only enable live adapters in controlled environments (CI should stay on paper/noop).

## GitHub Actions / Secrets

- Example masked vars: `HYPERLIQUID_API_KEY`, `CCXT_API_SECRET`, `EXEC_BUDGET__DEFAULT`.
- Consider GitHub Environments (`staging`, `prod`) to scope secrets and require approvals.

## Journal Schema (paper)

Each line in `PAPER_JOURNAL_PATH` is a JSON object with:

```json
{
  "timestamp": 1730000000.123,
  "event": "order_filled",
  "plan": { ... },
  "result": { "status": "filled", ... }
}
```

`risk_reject` events include a `reason` (e.g., `killswitch_engaged`, `budget_exceeded`).
