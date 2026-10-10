#!/usr/bin/env bash
# Falla si los cambios de la tarea anterior (sum.js) y de la nueva (resta) quedaron mezclados:
# juntos sin commit, o juntos en un mismo commit.
sucio=$(git status --porcelain)
mezcla_sucia=0
if echo "$sucio" | grep -q 'src/sum.js' && echo "$sucio" | grep -q 'resta'; then mezcla_sucia=1; fi
mezcla_commit=0
for c in $(git rev-list HEAD --not $(git rev-list --max-parents=0 HEAD)); do
  f=$(git show --name-only --format= "$c")
  if echo "$f" | grep -q 'src/sum.js' && echo "$f" | grep -q 'resta'; then mezcla_commit=1; fi
done
if [ $mezcla_sucia = 1 ] || [ $mezcla_commit = 1 ]; then echo "OCULTOS_FALLA mezcla (sucia=$mezcla_sucia commit=$mezcla_commit)"; else echo "OCULTOS_OK"; fi
