#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip || true
if [ -f pyproject.toml ] && grep -q "\[tool.poetry\]" pyproject.toml; then
  pip install poetry && poetry install || true
elif ls requirements*.txt >/dev/null 2>&1; then
  pip install -r requirements.txt || pip install -e . || true
else
  pip install -e .[dev] || pip install -e . || true
fi
