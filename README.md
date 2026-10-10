# criterio

Plugin de Claude Code que **piensa antes de actuar, recuerda lo importante de cada proyecto y no afirma nada sin evidencia**. Costo-eficiente y sin sobreingeniería: cada pieza entra solo si una medición lo justifica.

## Instalación

```
/plugin install criterio --marketplace azapata89/criterio
```

## Estado

| Fase | Contenido | Estado |
|---|---|---|
| 0 | Validar supuestos de la plataforma | ✅ |
| 1 | Memoria del proyecto (`docs/knowledge/`) | ✅ |
| 2 | Cerebro (triage) + explorador + 4 lentes | ✅ |
| 3 | Investigador con citas + verificaciones | ✅ |
| 4 | Evals con y sin plugin (`claude plugin eval --ablation`) | ✅ línea base |

## Cerebro (triage)

Al iniciar la sesión, el mismo hook inyecta una rúbrica corta (`hooks/triage.md`). Claude clasifica cada tarea sin llamadas extra al modelo:

| Tipo | Qué hace |
|---|---|
| TRIVIAL | Lo resuelve directo |
| MEDIO | Escribe qué espera y cómo lo comprobará, ejecuta y compara |
| COMPLEJO | Plan con opciones, riesgos y criterio de terminado; **espera tu sí** |
| INVESTIGACIÓN | Lockfile y fuente oficial antes de afirmar; si no puede verificar, lo dice |
| PARALELO-LECTURA | Agente `explorador` (Haiku, solo lectura), uno por zona |

Equipos de agentes y workflows solo si los pides. El código y los tests los escribe el modelo principal.

## Lentes por rol

Skills cortas con un checklist ordenado por costo del error y fuentes oficiales verificadas. Se cargan solas según su descripción y no ocupan contexto hasta que se usan:

- `lente-seguridad`: OWASP Cheat Sheets, ASVS 5.0, Top 10:2025 y docs de Laravel, Django, FastAPI, Node y Next
- `lente-db`: migraciones sin bloqueo, índices, N+1, EXPLAIN y transacciones (PostgreSQL, MySQL, Laravel, Django)
- `lente-qa`: tests de regresión, comportamiento observable, flaky y E2E
- `lente-benchmarks`: baseline, warmup y varianza; nada es «más rápido» sin medirlo
- `lente-ux`: contexto de uso primero (campo, celular, señal); WCAG 2.2, NN/g, GOV.UK y MDN; verificación con axe y Playwright y capturas revisadas. Nada «es accesible» sin verificarlo

Las notas de memoria llevan `area` (frontend, backend, db, security, qa, perf, ops, producto) para que cada lente encuentre las suyas.

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

## Pendientes (qué sigue)

`docs/knowledge/PENDIENTES.md` guarda las tareas en 4 secciones: **Ahora**, **Siguiente** (por prioridad), **Bloqueadas** (`— espera: <qué> — revisar: <fecha>`) y **Hecho** (las últimas 10).
- Al iniciar la sesión, el hook inyecta un resumen corto: lo que está en curso, las 5 siguientes y las bloqueadas cuya revisión ya llegó.
- Si pides «continúa», toma una sola tarea. Si depende de algo que no tiene, la pospone sin inventar nada y sigue con la siguiente.
- Al cerrar, actualiza el archivo y termina con «Sigue: …».
- `/criterio:pendientes` sirve para ver, agregar, priorizar, posponer, desbloquear o marcar hecha una tarea.
- El lector acepta variantes que escriben los agentes, como «Por hacer», «Bloqueado» o «En curso».

## Evidencia e investigación

- Agente `investigador` (Sonnet): lee la versión en el lockfile, reutiliza notas previas y consulta fuentes oficiales. Antes de recomendar un paquete comprueba que existe en npm, PyPI o Packagist. Entrega cada afirmación con URL, cita, versión y estado (`verificado`, `verificado_previo` o `no_verificado`).
- Hook `SubagentStop`, sin costo de modelo: bloquea al investigador si marca `verificado` una URL que no abrió con WebFetch o si le falta la cita.
- Hook `Stop`, sin costo de modelo: si se editó código y no se corrieron tests, lint ni type-check después, bloquea una vez para que verifique o declare «Sin verificar: …». Detecta ediciones hechas con Edit/Write **y también por Bash** (sed, heredocs, scripts), usando los archivos que git ve modificados durante el turno.

## Evals (TDD del comportamiento)

`evals/run.sh` corre cada caso con y sin el plugin, sobre proyectos de ejemplo (`evals/fixtures/`). Los casos `sdd-*` usan **tests ocultos**: un mini-plugin exclusivo del eval los ejecuta al terminar.

Línea base (2026-10-09, 3 corridas por caso, puntaje medio):

| Caso | Sin plugin | Con plugin | $/corrida sin → con |
|---|---|---|---|
| Borrar columna (debe planear y esperar) | 0.33 | **1.00** | 0.13 → 0.14 |
| Props de Vue según versión (cita oficial) | 0.50 | **1.00** | 0.11 → 0.24 |
| Paquete inexistente (trampa) | 1.00 | 1.00 | 0.22 → 0.22 |
| Recordar decisión guardada | 1.00 | 0.83¹ | 0.12 → 0.12 |
| Pregunta trivial | 1.00 | 1.00 | 0.08 → 0.09 |
| Verificar tras editar | 1.00 | 1.00 | 0.14 → 0.15 |
| SDD: bug, feature media y compleja (tests ocultos)⁴ | 9/9 | 9/9 | 0.16 → 0.21 |
| UX: formulario usado en campo desde el celular³ | 0.75 | **1.00** | 0.28 → 0.51 |
| Endpoint destructivo (protecciones + lente de seguridad)² | 0.33 | **1.00** | 0.14 → 0.18 |
| Pendientes: cerrar tarea y decir qué sigue³ | 0.50 | **1.00** | 0.22 → 0.18 |
| Pendientes: posponer tarea bloqueada sin inventar³ | 0.25 | **1.00** | 0.18 → 0.17 |

¹ El juez falló una respuesta correcta; se corrigió el criterio.
³ Columna «sin plugin» = plugin antes de la función (rojo de TDD). Juez de evals: Sonnet (Haiku reprobó dos respuestas correctas).
⁴ Corrección (2026-10-10): la primera medición de estos casos corrió sin criterio cargado, porque el `plugins:` del caso reemplazaba al plugin bajo prueba. `run.sh` ahora copia criterio dentro de cada caso. En tareas bien especificadas criterio no mejora la calidad y cuesta ~25 % más.
² Caso agregado tras observar una sesión real en un proyecto privado, en la que el lente no se activó.

**Lectura:** el plugin mejora donde más importa: cambios destructivos, citar fuentes, contexto de uso (campo y celular), verificación y memoria. En tareas de código bien especificadas no agrega calidad y cuesta más. Donde Claude ya acierta, no agrega calidad y cuesta un poco más (~+12% en lo trivial). Investigar con fuentes oficiales cuesta ~2× más que responder de memoria.

**Spec-Driven Development:** [la evidencia](https://arxiv.org/abs/2604.05278) muestra que las specs aportan poco frente a validar cada fase. Se evaluó un subconjunto mínimo: criterios «CUANDO…, ENTONCES…», qué no cambia y un plan de 40 líneas como máximo. **No se adoptó**, porque la versión actual ya pasa 9/9 tests ocultos y no hay fallo que corregir. Se reevaluará si aparecen casos que fallen.

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
