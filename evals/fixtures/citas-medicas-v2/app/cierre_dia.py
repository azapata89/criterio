from app.db import ejecutar


def cerrar_dia(dia):
    """Corre a medianoche: las citas del día que siguen agendadas quedan como no_asistio."""
    ejecutar(
        "UPDATE citas SET estado = 'no_asistio' WHERE fecha_hora::date = %s AND estado = 'agendada'",
        (dia,),
    )
