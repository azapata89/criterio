from app.db import ejecutar


def buscar_por_documento(documento):
    return ejecutar("SELECT * FROM pacientes WHERE documento = %s", (documento,))


def registrar(documento, nombre, fecha_nacimiento, telefono, municipio, regimen):
    return ejecutar(
        "INSERT INTO pacientes (documento, nombre, fecha_nacimiento, telefono, municipio, regimen) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (documento, nombre, fecha_nacimiento, telefono, municipio, regimen),
    )
