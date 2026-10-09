def total(items):
    """Total de un pedido. items: lista de (precio_unitario, cantidad)."""
    return sum(precio * cantidad for precio, cantidad in items)
