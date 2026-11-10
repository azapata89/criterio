from datetime import datetime

from app.db import ejecutar


def crear_cita(paciente_id, medico_id, fecha_hora, motivo=None):
    return ejecutar(
        "INSERT INTO citas (paciente_id, medico_id, fecha_hora, motivo) VALUES (%s, %s, %s, %s) RETURNING id",
        (paciente_id, medico_id, fecha_hora, motivo),
    )


def cancelar_cita(cita_id):
    ejecutar(
        "UPDATE citas SET estado = 'cancelada', cancelada_en = %s WHERE id = %s",
        (datetime.now(), cita_id),
    )


def reprogramar_cita(cita_id, nueva_fecha):
    ejecutar("UPDATE citas SET estado = 'reprogramada' WHERE id = %s", (cita_id,))
    fila = ejecutar("SELECT paciente_id, medico_id, motivo FROM citas WHERE id = %s", (cita_id,))
    return crear_cita(fila["paciente_id"], fila["medico_id"], nueva_fecha, fila["motivo"])


def agenda_del_dia(medico_id, dia):
    return ejecutar(
        "SELECT * FROM citas WHERE medico_id = %s AND fecha_hora::date = %s AND estado = 'agendada' ORDER BY fecha_hora",
        (medico_id, dia),
    )
