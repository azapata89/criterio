def descuento_por_volumen(cantidad):
    """Fracción de descuento por línea: 10% desde 50 unidades, 5% desde 10."""
    if cantidad >= 50:
        return 0.10
    if cantidad >= 10:
        return 0.05
    return 0.0


def total(items):
    """Total de un pedido con descuento por volumen. items: lista de (precio_unitario, cantidad)."""
    return sum(precio * cantidad * (1 - descuento_por_volumen(cantidad)) for precio, cantidad in items)
