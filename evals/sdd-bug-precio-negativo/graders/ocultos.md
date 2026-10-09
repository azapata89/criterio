---
type: regex
pattern: 'OCULTOS_OK'
match: contains
target: { source: file, path: .eval/resultado.txt }
---
Los tests ocultos pasan.
