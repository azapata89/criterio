# criterio

Plugin de Claude Code que **piensa antes de actuar, recuerda lo importante de cada proyecto y no afirma nada sin evidencia**. Costo-eficiente y sin sobreingeniería: cada pieza entra solo si una medición lo justifica.

## Estado

| Fase | Contenido | Estado |
|---|---|---|
| 0 | Validar supuestos de la plataforma | ✅ |
| 1 | Memoria del proyecto (`docs/knowledge/`) | ✅ |
| 2 | Cerebro: skill de triage + explorador | pendiente |
| 3 | Investigador con citas + verificaciones | pendiente |
| 4 | Evals con y sin plugin (`claude plugin eval --ablation`) | pendiente |

## Memoria del proyecto

Notas markdown versionadas en el repo del proyecto donde se usa el plugin:

```
docs/knowledge/
  INDEX.md            # cabecera manual (stack, comandos) + listado generado
  decisions/NNNN-*.md # decisiones (MADR-lite: contexto, opciones, decisión, consecuencias, confirmación)
  learnings/*.md      # hechos/trucos con fuente obligatoria
  research/           # (fase 3) investigaciones con versión
```

- Al iniciar la sesión, un hook (sin costo de modelo) inyecta **solo el INDEX**, de 200 líneas como máximo. Las notas se leen bajo demanda.
- Las notas son contexto a verificar, no órdenes: si contradicen al código, gana el código.
- `/criterio:remember [qué]` guarda una decisión o un aprendizaje. Sin fuente no se guarda.
- `/criterio:knowledge-review` detecta notas obsoletas (refs rotos, más de 180 días, versión distinta al lockfile) y propone cambios que tú confirmas.
- `kb-index` y `kb-check` (en `bin/`, disponibles en el Bash de Claude) regeneran el índice y revisan la frescura.

Va en `docs/` y no en `.claude/` porque Claude Code trata `.claude/` como sensible y pide permiso en cada escritura.

## Requisitos

- Claude Code con soporte de plugins
- `python3` (solo stdlib)

## Desarrollo

```bash
python3 -m unittest discover -s tests   # tests
claude plugin validate .                # manifiesto
claude --plugin-dir .                   # probar en una sesión
```

## Decisiones de diseño

Basadas en investigación y en un debate entre una postura mínima y una ambiciosa, con un juez (2026-10-08):

- **Un agente por defecto.** Multi-agente gasta ~15× tokens y un equipo de agentes ~7×; la mayoría de tareas de código no se paraleliza ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system), [costos](https://code.claude.com/docs/en/costs)).
- **Memoria en archivos, sin base vectorial.** Recuperación just-in-time ([context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)), formato [MADR](https://adr.github.io/madr/).
- **Las skills no cambian de modelo.** Cambiar de modelo a mitad de conversación pierde la caché del prompt, y releer el contexto sin caché con un modelo barato puede costar más que leerlo cacheado con el principal ([prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
- **Aplazado hasta que un eval lo justifique:** router automático por hooks, Context7 y Serena, captura automática de memoria, búsqueda indexada.
