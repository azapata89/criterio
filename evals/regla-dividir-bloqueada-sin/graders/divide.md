---
type: llm
---
El agente hace la parte que no depende de las credenciales (script de respaldo y una prueba local sin el bucket real, por ejemplo con un directorio o un servidor S3 local) y deja registrado como bloqueado SOLO lo que espera las credenciales/bucket (con qué espera). No marca toda la tarea como bloqueada sin avanzar, ni inventa credenciales o nombres de bucket.
