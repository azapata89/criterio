#!/usr/bin/env bash
# Corre la suite de evals con y sin el plugin. Uso: evals/run.sh [--runs N] [--case glob] [...]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
# Los casos con tests ocultos declaran `plugins:` (eval-hooks), y eso reemplaza al plugin bajo
# prueba en vez de sumarse. Por eso cada uno lleva una copia fresca de criterio en `criterio/`.
for caso in evals/*/; do
  if grep -q '"criterio"' "$caso/prompt.md" 2>/dev/null; then
    rm -rf "$caso/criterio" && mkdir -p "$caso/criterio"
    tar -c --exclude=./evals --exclude=./tests --exclude=./.git . | tar -x -C "$caso/criterio"
  fi
done
exec claude plugin eval . --scaffold --trust-plugin --no-publish \
  --allow-tools Edit Write Bash WebFetch WebSearch \
  --judge-model "${EVAL_JUDGE:-sonnet}" \
  --max-cost-usd "${EVAL_MAX_COST:-15}" "$@"
