
import os
import sqlite3


RUTA_BASE_DATOS = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "biblioteca.db"
    )
)


# =================================
# SEDES
# =================================

def crear_tabla_sedes(ruta=None):
    conexion = sqlite3.connect(ruta or RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sedes (
            id_sede INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            direccion TEXT NOT NULL,
            telefono TEXT NOT NULL,
            horarios TEXT NOT NULL,
            activa INTEGER NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


def guardar_sede(sede):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id_sede FROM sedes WHERE id_sede = ?",
        (sede.id_sede,)
    )

    if cursor.fetchone() is not None:
        conexion.close()
        return False

    cursor.execute("""
        INSERT INTO sedes
        (id_sede, nombre, direccion, telefono, horarios, activa)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        sede.id_sede,
        sede.nombre,
        sede.direccion,
        sede.telefono,
        sede.horarios,
        sede.activa
    ))

    conexion.commit()
    conexion.close()

    return True


def consultar_sedes():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id_sede, nombre, direccion,
               telefono, horarios, activa
        FROM sedes
        ORDER BY id_sede
    """)

    sedes = cursor.fetchall()
    conexion.close()

    return sedes


def actualizar_estado_sede(sede):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute(
        "UPDATE sedes SET activa = ? WHERE id_sede = ?",
        (sede.activa, sede.id_sede)
    )

    conexion.commit()
    conexion.close()


def actualizar_datos_sede(sede):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE sedes
        SET nombre = ?,
            direccion = ?,
            telefono = ?,
            horarios = ?
        WHERE id_sede = ?
    """, (
        sede.nombre,
        sede.direccion,
        sede.telefono,
        sede.horarios,
        sede.id_sede
    ))

    conexion.commit()
    conexion.close()


# =================================
# SOCIOS
# =================================

def crear_tabla_socios(ruta=None):
    conexion = sqlite3.connect(ruta or RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            id_socio INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT NOT NULL,
            habilitado INTEGER NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


def guardar_socio(socio):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id_socio FROM socios WHERE documento = ?",
        (socio.documento,)
    )

    if cursor.fetchone() is not None:
        conexion.close()
        return False

    cursor.execute("""
        INSERT INTO socios
        (documento, nombre, apellido, telefono, correo, habilitado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        socio.documento,
        socio.nombre,
        socio.apellido,
        socio.telefono,
        socio.correo,
        socio.habilitado
    ))

    conexion.commit()
    conexion.close()

    return True


def consultar_socios():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id_socio, documento, nombre, apellido,
               telefono, correo, habilitado
        FROM socios
        ORDER BY apellido, nombre
    """)

    socios = cursor.fetchall()
    conexion.close()

    return socios


def actualizar_datos_socio(socio):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE socios
        SET nombre = ?,
            apellido = ?,
            telefono = ?,
            correo = ?
        WHERE id_socio = ?
    """, (
        socio.nombre,
        socio.apellido,
        socio.telefono,
        socio.correo,
        socio.id_socio
    ))

    conexion.commit()
    conexion.close()


def actualizar_estado_socio(socio):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute(
        "UPDATE socios SET habilitado = ? WHERE id_socio = ?",
        (socio.habilitado, socio.id_socio)
    )

    conexion.commit()
    conexion.close()
