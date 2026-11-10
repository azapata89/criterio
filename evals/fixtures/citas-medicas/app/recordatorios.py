from datetime import datetime, timedelta

from app.db import ejecutar
from app.sms import enviar_sms


def enviar_recordatorios():
    """Corre cada hora: avisa por SMS las citas de dentro de 24 h."""
    desde = datetime.now() + timedelta(hours=23)
    hasta = datetime.now() + timedelta(hours=24)
    citas = ejecutar(
        "SELECT c.id, p.telefono, c.fecha_hora FROM citas c JOIN pacientes p ON p.id = c.paciente_id "
        "WHERE c.estado = 'agendada' AND c.fecha_hora BETWEEN %s AND %s",
        (desde, hasta),
    )
    for cita in citas:
        entregada = enviar_sms(cita["telefono"], f"Recuerde su cita el {cita['fecha_hora']:%d/%m %H:%M}")
        ejecutar(
            "INSERT INTO notificaciones (cita_id, canal, enviada_en, entregada) VALUES (%s, 'sms', %s, %s)",
            (cita["id"], datetime.now(), entregada),
        )
