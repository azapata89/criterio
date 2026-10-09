---
name: remember
description: Guarda en la base de conocimiento del proyecto (docs/knowledge/) una decisión o un aprendizaje verificado, con fuente. Úsala cuando el usuario pida recordar, anotar o registrar algo, o para inicializar la base del proyecto.
argument-hint: "[qué recordar]"
disable-model-invocation: true
---

# Guardar conocimiento del proyecto

Objetivo: dejar una nota corta, verificable y con fuente que sirva en futuras sesiones. Calidad sobre cantidad: si no vale la pena recordarlo dentro de 3 meses, no se guarda.

## 1. Asegurar la base
Si no existe `docs/knowledge/INDEX.md`:
1. Ejecuta `kb-index --init`.
2. Rellena las secciones **Stack** y **Comandos** del INDEX leyendo los manifiestos reales del proyecto (`package.json`, `composer.json`, `pyproject.toml`/`requirements*.txt` y sus lockfiles). Solo versiones que aparezcan en esos archivos; no supongas ninguna. Máximo ~15 líneas.

## 2. Decidir qué guardar
A partir de `$ARGUMENTS` o, si viene vacío, de la conversación reciente, elige el tipo:
- **decision** (`decisions/NNNN-slug.md`): una elección de diseño con alternativas. NNNN = siguiente número libre.
- **learning** (`learnings/slug.md`): un hecho, truco o problema del stack o del proyecto.

No guardes:
- lo que ya está en el código, el README, CLAUDE.md o git;
- lo que solo importa en esta conversación;
- secretos ni credenciales.

Antes de crear una nota, busca con Grep en `docs/knowledge/` si ya hay una sobre el tema. Si la hay, actualízala en vez de duplicarla. Si la nueva la contradice, marca la vieja `status: superseded` y pon `superseded_by: <ruta nueva>`.

## 3. Escribir con evidencia
Usa la plantilla `templates/decision.md` o `templates/learning.md` del directorio de esta skill.
- `sources`: obligatorio en learnings. Cada fuente debe ser algo que tú hayas visto en esta sesión: una URL consultada o un `archivo:línea` leído. Si no hay fuente, **no guardes la nota**; dile al usuario qué haría falta para verificarla.
- `refs`: solo rutas que existan hoy en el repo.
- `area`: una de frontend, backend, db, security, qa, perf, ops, producto. Sirve para que los lentes encuentren las notas de su área.
- `verified_at`: fecha de hoy.
- Lenguaje simple; cada sección en 1-4 líneas.

## 4. Cerrar
1. Ejecuta `kb-index` para regenerar el índice.
2. Muestra al usuario la ruta de la nota y un resumen de una línea.
