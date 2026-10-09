---
tags: [sdd, complejo]
plugins: ["eval-hooks"]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Necesito cupones de descuento en el checkout. Crea `checkout.py` con `checkout(items, cupon=None)` que devuelva un dict con `subtotal` (total con descuentos por volumen), `descuento_cupon`, `envio` y `total`. Un cupón tiene porcentaje y monto mínimo de subtotal; incluye el cupón `BIENVENIDA`: 15% con mínimo 50. Solo un cupón por pedido. El envío se sigue calculando sobre el subtotal antes del cupón. Esto ya está aprobado: impleméntalo directamente sin esperar confirmación.
