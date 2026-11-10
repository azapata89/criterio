from datetime import datetime

from app.db import ejecutar


def registrar_llegada(cita_id, valor_copago):
    """El paciente llega a recepción: paga el copago y la cita queda atendida."""
    ejecutar(
        "INSERT INTO pagos (cita_id, valor, pagado_en) VALUES (%s, %s, %s)",
        (cita_id, valor_copago, datetime.now()),
    )
    ejecutar("UPDATE citas SET estado = 'atendida' WHERE id = %s", (cita_id,))
