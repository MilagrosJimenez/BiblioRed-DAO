"""Carga de datos realista para reportes y defensa del TP.

No modifica clases ni consultas SQL; solo genera un conjunto de préstamos,
remitos y devoluciones sobre la base local bibliotec.db del proyecto.
"""

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "biblioteca.db"


def limpiar_tablas(conexion):
    cursor = conexion.cursor()
    for tabla in [
        "historial_retornos",
        "remitos_retorno",
        "devoluciones",
        "prestamos",
        "historial_remitos",
        "remitos",
        "solicitudes_prestamo",
    ]:
        cursor.execute(f"DELETE FROM {tabla}")
    conexion.commit()


def cargar_datos():
    conexion = sqlite3.connect(DB)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    limpiar_tablas(conexion)

    solicitudes = [
        (1, 1, 1, 901, 902, "Interbibliotecario", "Recibida en destino", "2026-11-01"),
        (2, 2, 4, 903, 901, "Interbibliotecario", "Recibida en destino", "2026-11-02"),
        (3, 3, 9, 901, 903, "Interbibliotecario", "Recibida en destino", "2026-11-03"),
        (4, 4, 12, 901, 902, "Interbibliotecario", "Recibida en destino", "2026-11-04"),
        (5, 5, 14, 901, 903, "Local", "Prestada", "2026-11-05"),
        (6, 6, 15, 902, 902, "Local", "Prestada", "2026-11-06"),
        (7, 1, 17, 901, 902, "Interbibliotecario", "Recibida en destino", "2026-11-07"),
        (8, 3, 18, 902, 902, "Local", "Prestada", "2026-11-08"),
        (9, 2, 22, 903, 903, "Local", "Prestada", "2026-11-09"),
        (10, 5, 23, 901, 901, "Local", "Prestada", "2026-11-10"),
        (11, 4, 10, 902, 901, "Interbibliotecario", "Recibida en destino", "2026-11-11"),
        (12, 7, 20, 903, 903, "Local", "Prestada", "2026-11-12"),
    ]
    cursor.executemany(
        """
        INSERT INTO solicitudes_prestamo
        (id_solicitud, id_socio, id_ejemplar, id_sede_origen, id_sede_destino, tipo, estado, fecha_solicitud)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        solicitudes,
    )

    prestamos = [
        (1, 1, 1, 1, "2026-11-01", "2026-11-15", None, "Activo"),
        (2, 2, 2, 4, "2026-11-02", "2026-11-16", None, "Activo"),
        (3, 3, 3, 9, "2026-11-03", "2026-11-17", None, "Activo"),
        (4, 4, 4, 12, "2026-10-10", "2026-10-25", None, "Activo"),
        (5, 5, 5, 14, "2026-05-12", "2026-05-26", "2026-05-17", "Devuelto"),
        (6, 6, 6, 15, "2026-06-05", "2026-06-19", "2026-06-08", "Devuelto"),
        (7, 7, 1, 17, "2026-11-07", "2026-11-21", None, "Activo"),
        (8, 8, 3, 18, "2026-07-20", "2026-08-03", "2026-07-27", "Devuelto"),
        (9, 9, 2, 22, "2026-08-15", "2026-08-29", "2026-08-20", "Devuelto"),
        (10, 10, 5, 23, "2026-11-08", "2026-11-22", None, "Activo"),
        (11, 11, 4, 10, "2026-10-28", "2026-11-11", None, "Activo"),
    ]
    cursor.executemany(
        """
        INSERT INTO prestamos
        (id_prestamo, id_solicitud, id_socio, id_ejemplar, fecha_prestamo, fecha_vencimiento, fecha_devolucion, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        prestamos,
    )

    devoluciones = [
        (1, 5, 14, 903, "2026-05-17", "Bueno", "Devolución sin desperfectos"),
        (2, 6, 15, 902, "2026-06-08", "Bueno", "Retorno a sede propia"),
        (3, 8, 18, 902, "2026-07-27", "Bueno", "Se recibió en la sede local"),
        (4, 9, 22, 903, "2026-08-20", "Bueno", "Ejemplar en condiciones aceptables"),
    ]
    cursor.executemany(
        """
        INSERT INTO devoluciones
        (id_devolucion, id_prestamo, id_ejemplar, id_sede_recepcion, fecha, estado_fisico, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        devoluciones,
    )

    remitos = [
        (1, 1, 1, 901, 902, "Recibido", "2026-11-01 08:30:00"),
        (2, 2, 4, 903, 901, "Recibido", "2026-11-02 09:00:00"),
        (3, 3, 9, 901, 903, "Recibido", "2026-11-03 07:15:00"),
        (4, 4, 12, 901, 902, "Recibido", "2026-11-04 06:45:00"),
        (5, 7, 17, 901, 902, "Recibido", "2026-11-07 11:00:00"),
        (6, 11, 10, 902, 901, "Recibido", "2026-11-11 13:15:00"),
    ]
    cursor.executemany(
        """
        INSERT INTO remitos
        (id_remito, id_solicitud, id_ejemplar, id_sede_origen, id_sede_destino, estado, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        remitos,
    )

    historial_remitos = [
        (1, 1, "En tránsito", "2026-11-01 09:00:00", "Envío despegado desde Demo Centro"),
        (2, 1, "Recibido", "2026-11-02 10:00:00", "Recibido en Demo Norte"),
        (3, 2, "En tránsito", "2026-11-02 09:30:00", "Despacho desde Demo Sur"),
        (4, 2, "Recibido", "2026-11-03 11:00:00", "En destino y listo para préstamo"),
        (5, 3, "En tránsito", "2026-11-03 08:00:00", "Traslado de Demo Centro"),
        (6, 3, "Recibido", "2026-11-04 12:00:00", "Recepción en Demo Sur"),
        (7, 4, "En tránsito", "2026-11-04 07:30:00", "Salida desde centro"),
        (8, 4, "Recibido", "2026-11-05 09:00:00", "Recibido en norte"),
        (9, 5, "En tránsito", "2026-11-07 11:30:00", "Ejemplar listo para traslado"),
        (10, 5, "Recibido", "2026-11-08 10:45:00", "Recibido en Demo Norte"),
        (11, 6, "En tránsito", "2026-11-11 13:40:00", "Retiro desde Demo Norte"),
        (12, 6, "Recibido", "2026-11-12 15:00:00", "Ingreso a Demo Centro"),
    ]
    cursor.executemany(
        """
        INSERT INTO historial_remitos
        (id_historial, id_remito, estado, fecha, observacion)
        VALUES (?, ?, ?, ?, ?)
        """,
        historial_remitos,
    )

    remitos_retorno = [
        (1, 1, 14, 903, 901, "Recibido", "2026-05-17 15:00:00"),
        (2, 2, 15, 902, 902, "Recibido", "2026-06-08 13:30:00"),
        (3, 3, 18, 902, 902, "Recibido", "2026-07-27 16:00:00"),
        (4, 4, 22, 903, 903, "Recibido", "2026-08-20 17:30:00"),
    ]
    cursor.executemany(
        """
        INSERT INTO remitos_retorno
        (id_remito, id_devolucion, id_ejemplar, id_sede_origen, id_sede_destino, estado, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        remitos_retorno,
    )

    historial_retornos = [
        (1, 1, "En tránsito", "2026-05-17 15:15:00", "Revisión y retiro desde Demo Sur"),
        (2, 1, "Recibido", "2026-05-18 11:00:00", "Regreso exitoso a Demo Centro"),
        (3, 2, "En tránsito", "2026-06-08 13:45:00", "Cierre de devolución local"),
        (4, 2, "Recibido", "2026-06-09 10:00:00", "Recepción en la misma sede"),
        (5, 3, "En tránsito", "2026-07-27 16:15:00", "Retorno de ejemplar local"),
        (6, 3, "Recibido", "2026-07-28 09:00:00", "Ejemplar en stock"),
        (7, 4, "En tránsito", "2026-08-20 17:45:00", "Despacho a sede propietaria"),
        (8, 4, "Recibido", "2026-08-21 12:00:00", "Devolución registrada"),
    ]
    cursor.executemany(
        """
        INSERT INTO historial_retornos
        (id_historial, id_remito, estado, fecha, observacion)
        VALUES (?, ?, ?, ?, ?)
        """,
        historial_retornos,
    )

    actualizaciones = [
        ("Prestado", 902, 1),
        ("Prestado", 901, 4),
        ("Prestado", 903, 9),
        ("Prestado", 902, 12),
        ("Disponible", 901, 14),
        ("Disponible", 902, 15),
        ("Prestado", 902, 17),
        ("Disponible", 902, 18),
        ("Disponible", 903, 22),
        ("Prestado", 901, 23),
        ("Prestado", 901, 10),
        ("Disponible", 903, 20),
    ]
    cursor.executemany(
        "UPDATE ejemplares SET estado = ?, id_sede_actual = ? WHERE id_ejemplar = ?",
        actualizaciones,
    )

    conexion.commit()
    print("Solicitudes:", cursor.execute("SELECT COUNT(*) FROM solicitudes_prestamo").fetchone()[0])
    print("Prestamos activos:", cursor.execute("SELECT COUNT(*) FROM prestamos WHERE estado = 'Activo'").fetchone()[0])
    print("Prestamos devueltos:", cursor.execute("SELECT COUNT(*) FROM prestamos WHERE estado = 'Devuelto'").fetchone()[0])
    print("Remitos:", cursor.execute("SELECT COUNT(*) FROM remitos").fetchone()[0])
    print("Remitos de retorno:", cursor.execute("SELECT COUNT(*) FROM remitos_retorno").fetchone()[0])
    print("Devoluciones:", cursor.execute("SELECT COUNT(*) FROM devoluciones").fetchone()[0])
    conexion.close()


if __name__ == "__main__":
    cargar_datos()
