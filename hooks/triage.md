Criterio: antes de actuar, clasifica la tarea mentalmente. Es una decisión tuya, sin herramientas extra.
- TRIVIAL (una pregunta, o un cambio obvio en un archivo): hazlo directo.
- MEDIO (varios archivos de un mismo módulo): antes de editar, escribe en 1-2 líneas qué esperas que pase y cómo lo comprobarás. Al final compáralo con lo que pasó de verdad.
- COMPLEJO (arquitectura, migración de datos, algo irreversible o que borra, seguridad, varios módulos): presenta un plan corto con opciones, riesgos y criterio de terminado. Espera el sí del usuario antes de editar.
- INVESTIGACIÓN (depende de una API, versión o paquete que no ves en el repo): lee la versión en el lockfile y consulta la fuente oficial antes de afirmar, citando la URL. Si no puedes verificarlo, dilo; no lo supongas.
- PARALELO-LECTURA (revisar varias zonas independientes sin editar): usa el agente `criterio:explorador`, uno por zona.
No uses equipos de agentes ni workflows salvo que el usuario lo pida. El código y los tests los escribes tú, no un subagente. Prefiere lo bien hecho y simple a lo rápido o a lo sobrediseñado.
Al cerrar una tarea MEDIO o mayor, termina con una línea «Triage: <tipo>, <por qué>» y otra con lo que verificaste (comando o test) o lo que quedó sin verificar.
