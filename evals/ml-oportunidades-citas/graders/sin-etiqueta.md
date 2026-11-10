---
type: llm
---
La respuesta detecta, citando el esquema o el código (por ejemplo `citas.estado` en `db/schema.sql`), que el sistema no registra si el paciente asistió o no a la cita, y concluye que hoy no se puede entrenar un modelo de inasistencia. Propone como primer paso concreto empezar a registrar la asistencia (por ejemplo, un estado de asistió/no asistió o un check-in) y acumular historia. Falla si propone entrenar el modelo con los datos actuales o si infiere la inasistencia de citas que siguen como «agendada» sin advertir que eso no es una etiqueta confiable.
