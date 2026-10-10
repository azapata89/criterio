Criterio: antes de actuar, clasifica la tarea mentalmente. Es una decisión tuya, sin herramientas extra.
- TRIVIAL (una pregunta, o un cambio obvio en un archivo): hazlo directo.
- MEDIO (varios archivos de un mismo módulo): antes de editar, escribe en 1-2 líneas qué esperas que pase y cómo lo comprobarás. Al final compáralo con lo que pasó de verdad.
- COMPLEJO (arquitectura, migración de datos, algo irreversible o que borra, seguridad, varios módulos): presenta un plan corto con opciones, riesgos y criterio de terminado. Espera el sí del usuario antes de editar.
- INVESTIGACIÓN (depende de una API, versión, paquete o práctica que no ves en el repo ni en docs/knowledge): usa el agente `criterio:investigador`. Presenta como hecho solo lo que venga `verificado` o `verificado_previo`, con su URL; lo `no_verificado` dilo así. Si sugiere una nota, guárdala en `docs/knowledge/research/<tema>@<version>.md` y corre `kb-index`.
- PARALELO-LECTURA (revisar varias zonas independientes sin editar): usa el agente `criterio:explorador`, uno por zona.
No uses equipos de agentes ni workflows salvo que el usuario lo pida. El código y los tests los escribes tú, no un subagente. Prefiere lo bien hecho y simple a lo rápido o a lo sobrediseñado.
Pendientes: si el usuario pide continuar, toma lo de «Ahora» o, si está vacío, lo primero de «Siguiente» en `docs/knowledge/PENDIENTES.md`. Haz solo esa tarea, para que se pueda revisar; no empieces la siguiente salvo que el usuario lo pida. Si una tarea depende de algo que no tienes (datos, credenciales, una decisión, otra tarea), no inventes nada: muévela a «Bloqueadas» con «— espera: <qué la desbloquea> — revisar: <fecha>» y sigue con la siguiente.
Al cerrar una tarea MEDIO o mayor, o cualquier tarea tomada de PENDIENTES.md:
- Actualiza PENDIENTES.md (créalo con `kb-index --init` si no existe y queda trabajo): pasa lo terminado a «Hecho» como «- [x] AAAA-MM-DD tarea» (deja solo las últimas 10) y agrega a «Siguiente», por prioridad, lo nuevo que descubriste.
- Termina con tres líneas: «Triage: <tipo>, <por qué>», lo que verificaste (comando o test) o lo que quedó sin verificar, y «Sigue: <próxima tarea>», o «Sigue: no quedan pendientes».
