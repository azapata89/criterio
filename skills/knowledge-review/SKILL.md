---
name: knowledge-review
description: Revisa la base de conocimiento del proyecto (docs/knowledge/) para detectar notas obsoletas, refs rotos, versiones desactualizadas o notas sin fuente, y propone correcciones que el usuario confirma.
disable-model-invocation: true
---

# Revisar la base de conocimiento

Objetivo: que lo guardado siga siendo cierto. Esta skill no cambia nada sin confirmación del usuario.

## 1. Detectar
1. Ejecuta `kb-check`. Lista refs rotos, verificaciones viejas, notas `stale` y learnings sin fuentes.
2. Para cada nota activa con campo `version`, compárala con la versión del lockfile del proyecto (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `composer.lock`, `poetry.lock`, `uv.lock`, `requirements*.txt`). Si difieren, la nota es candidata a revisión.
3. Para las decisiones, ejecuta su sección **Confirmación** si es barata: un grep o una lectura de archivo. No corras suites largas sin preguntar.

## 2. Proponer
Muestra una tabla corta con estas columnas: nota, problema, propuesta. La propuesta es una de cuatro:
- **actualizar**: corregir refs o versión y refrescar `verified_at`.
- **re-verificar**: hace falta consultar la fuente de nuevo.
- **superseded**: otra nota la reemplaza.
- **borrar**: ya no aporta.

Re-verificar significa volver a la fuente citada. Si no puedes comprobarla, dilo; no refresques `verified_at` sin haber verificado.

## 3. Aplicar
Aplica solo lo que el usuario apruebe. Después ejecuta `kb-index` y resume en una línea qué cambió.
