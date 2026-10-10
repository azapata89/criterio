---
type: regex
pattern: '-m unittest(\s+-v)?(\s+discover)?\s*(2>|\||;|&|"|$)|pytest\s*(-q\s*)?(2>|\||;|&|"|$)'
flags: m
match: contains
target: trace
---
Antes de cerrar corre la suite completa una vez (unittest sin módulos = discover).
