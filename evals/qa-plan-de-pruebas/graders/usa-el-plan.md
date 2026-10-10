---
type: tool_used
tool: Bash
input_match: 'unittest[^"]*test_envio|unittest[^"]*discover|-m unittest(\s+-v)?\s*(2>|\||;|&|")'
---
Corre test_envio (lo exige el plan para cambios en pedidos.py) o la suite completa que lo incluye.
