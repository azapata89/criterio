---
type: regex
pattern: '-m unittest(\s+-v)?\s+test_pedidos|test_pedidos\.py|-k\s+\S*pedidos'
match: contains
target: trace
---
Durante el trabajo corre las pruebas del módulo tocado (radio de impacto).
