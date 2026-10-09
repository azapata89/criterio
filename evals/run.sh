#!/usr/bin/env bash
# Corre la suite de evals con y sin el plugin. Uso: evals/run.sh [--runs N] [--case glob] [...]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec claude plugin eval . --scaffold --trust-plugin --no-publish \
  --allow-tools Edit Write Bash WebFetch WebSearch \
  --max-cost-usd "${EVAL_MAX_COST:-15}" "$@"
