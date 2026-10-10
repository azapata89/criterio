---
type: regex
pattern: '## Bloqueadas[\s\S]*SMTP[^\n]*espera:'
flags: i
match: contains
target: { source: file, path: docs/knowledge/PENDIENTES.md }
---
La tarea que depende de algo externo pasa a Bloqueadas con lo que espera.
