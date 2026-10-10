Criterio: antes de actuar, clasifica la tarea (decisión tuya, sin herramientas extra).
- TRIVIAL (pregunta o cambio obvio en 1 archivo): directo.
- MEDIO (varios archivos de un módulo): escribe antes qué esperas y cómo lo comprobarás; al final compáralo.
- COMPLEJO (arquitectura, migración de datos, irreversible/borra, seguridad, varios módulos): plan corto con opciones, riesgos y criterio de terminado; espera el sí del usuario.
- INVESTIGACIÓN (API, versión, paquete o práctica que no está en el repo ni en docs/knowledge): agente `criterio:investigador`; como hecho solo lo `verificado`/`verificado_previo` con URL. Si sugiere nota: `docs/knowledge/research/<tema>@<version>.md` + `kb-index`.
- PARALELO-LECTURA (zonas independientes, sin editar): `criterio:explorador`, uno por zona.
Sin equipos ni workflows salvo pedido. El código y los tests los escribes tú. Bien hecho y simple antes que rápido o sobrediseñado.
Pendientes (`docs/knowledge/PENDIENTES.md`): «continúa» = lo de «Ahora» o lo primero de «Siguiente», una tarea a la vez. No empieces otra con cambios sin commit de la anterior: commit si está autorizado, si no pregunta. Lo que depende de algo que no tienes (datos, credenciales, una decisión tuya o del usuario) va a «Bloqueadas» con «— espera: <qué> — revisar: <fecha>», sin inventar; si solo una parte espera, divide la tarea.
Al cerrar (MEDIO o mayor, o tarea de PENDIENTES): actualiza PENDIENTES (lo hecho a «Hecho» con fecha, máx. 10; lo nuevo a «Siguiente»); si hiciste push, revisa el CI o decláralo sin verificar. Termina con «Triage: <tipo>, <por qué>», lo verificado o sin verificar, y «Sigue: <próxima tarea>» (o «no quedan pendientes»).
