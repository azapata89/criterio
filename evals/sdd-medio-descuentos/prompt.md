---
tags: [sdd, medio]
plugins: ["eval-hooks", "criterio"]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Agrega descuentos por volumen a `total()` en pedidos.py: por línea, 10 o más unidades tienen 5% de descuento y 50 o más unidades tienen 10%.
