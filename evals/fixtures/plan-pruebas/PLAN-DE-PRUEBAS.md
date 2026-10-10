# Plan de pruebas

Qué correr según lo que cambia. Lo compartido dispara la suite completa.

| Si cambia | Correr |
|---|---|
| `pedidos.py` | `python3 -m unittest test_pedidos test_envio` (el envío se calcula sobre el total del pedido) |
| `envio.py` | `python3 -m unittest test_envio` |
| cualquier otra cosa o algo no listado | `python3 -m unittest discover` (suite completa, ~30 s) |

Antes de cerrar una tarea o hacer push: suite completa una vez.
