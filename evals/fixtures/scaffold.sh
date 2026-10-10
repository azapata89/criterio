#!/usr/bin/env bash
# Copia una o varias fixtures (en orden) al directorio de trabajo y hace un commit inicial.
# Si alguna fixture trae .eval/despues-del-commit.sh, se ejecuta después del commit.
# Uso: scaffold.sh <fixture> [<fixture>...]
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for f in "$@"; do cp -R "$here/$f/." .; done
git init -q && git add -A && git -c user.name=eval -c user.email=eval@local commit -qm fixture
if [ -f .eval/despues-del-commit.sh ]; then bash .eval/despues-del-commit.sh; fi
