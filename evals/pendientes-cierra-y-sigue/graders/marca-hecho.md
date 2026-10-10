---
type: regex
pattern: '## Hecho[\s\S]*\[x\][^\n]*sum'
match: contains
target: { source: file, path: docs/knowledge/PENDIENTES.md }
---
La tarea terminada queda marcada en Hecho.
