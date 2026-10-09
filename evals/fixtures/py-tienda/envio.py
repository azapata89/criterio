def costo_envio(total_pedido):
    """Envío gratis desde 100; si no, tarifa plana de 10."""
    return 0 if total_pedido >= 100 else 10
