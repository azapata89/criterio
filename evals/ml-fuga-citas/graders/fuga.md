---
type: llm
---
Si la respuesta propone predecir la inasistencia, advierte que el pago del copago (tabla `pagos`, que se registra en `app/recepcion.py` cuando el paciente llega) no puede usarse como variable para predecir si esa cita tendrá inasistencia, porque solo existe después de la llegada (fuga de datos). Falla si lo propone como variable o si no lo advierte. Si la respuesta no propone predecir la inasistencia, pasa solo si justifica por qué no.
