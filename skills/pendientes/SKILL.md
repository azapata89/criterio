---
name: pendientes
description: Muestra y organiza los pendientes del proyecto (docs/knowledge/PENDIENTES.md): ver, agregar, priorizar, posponer una tarea bloqueada indicando qué espera, desbloquear o marcar hecha. Úsala cuando el usuario pida ver, reordenar o posponer pendientes.
argument-hint: "[ver | agregar <tarea> | priorizar <tarea> | posponer <tarea> por <motivo> hasta <fecha> | desbloquear <tarea> | hecha <tarea>]"
disable-model-invocation: true
---

# Pendientes del proyecto

El archivo es `docs/knowledge/PENDIENTES.md`. Si no existe, créalo con `kb-index --init`.

## Formato
Respeta el formato, porque un hook lo lee al iniciar cada sesión:
```
## Ahora          ← una tarea, la que está en curso
## Siguiente      ← en orden de prioridad, la primera es la próxima
## Bloqueadas     ← - [ ] tarea — espera: <qué la desbloquea> — revisar: AAAA-MM-DD
## Hecho          ← - [x] AAAA-MM-DD tarea (solo las últimas 10)
```
Cada tarea va en una línea, con un verbo y un resultado verificable. Si la tarea viene de un plan o una decisión, cita la fuente entre paréntesis, por ejemplo `(0004·F0)`.

## Acciones según `$ARGUMENTS`
- **ver**, o sin argumentos: muestra Ahora, los 5 primeros de Siguiente y las bloqueadas, marcando las que tienen la fecha de revisión vencida. Para cada una de esas, pregunta si ya llegó lo que esperaba.
- **agregar**: inserta la tarea en Siguiente según su prioridad. Si no es obvia, pregunta antes de ubicarla.
- **priorizar**: la mueve al lugar indicado, o a Ahora si el usuario dice que es lo próximo.
- **posponer**: la mueve a Bloqueadas con `espera:` y `revisar:`. Si el usuario no da fecha, propone una. Si solo una parte espera algo, divide la tarea y deja en Siguiente lo que se puede hacer ya.
- **desbloquear**: la saca de Bloqueadas y la vuelve a poner en Siguiente.
- **hecha**: la mueve a Hecho con la fecha de hoy, solo si se verificó. Si no se verificó, pregunta.

Al terminar, muestra en 3 a 6 líneas cómo quedó: Ahora, lo próximo y las bloqueadas.
