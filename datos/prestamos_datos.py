
import sqlite3

from datos.base_datos import RUTA_BASE_DATOS


def crear_tabla_solicitudes(ruta=None):
    conexion = sqlite3.connect(ruta or RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_prestamo (
            id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            id_socio INTEGER NOT NULL,
            id_ejemplar INTEGER NOT NULL,
            id_sede_origen INTEGER NOT NULL,
            id_sede_destino INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            estado TEXT NOT NULL,
            fecha_solicitud TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (id_socio) REFERENCES socios(id_socio),
            FOREIGN KEY (id_ejemplar) REFERENCES ejemplares(id_ejemplar),
            FOREIGN KEY (id_sede_origen) REFERENCES sedes(id_sede),
            FOREIGN KEY (id_sede_destino) REFERENCES sedes(id_sede)
        )
    """)

    conexion.commit()
    conexion.close()


def consultar_solicitudes():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT sp.id_solicitud,
               s.apellido || ', ' || s.nombre,
               s.documento,
               e.codigo,
               l.titulo,
               origen.nombre,
               destino.nombre,
               sp.tipo,
               sp.estado,
               sp.fecha_solicitud
        FROM solicitudes_prestamo sp
        JOIN socios s ON s.id_socio = sp.id_socio
        JOIN ejemplares e ON e.id_ejemplar = sp.id_ejemplar
        JOIN libros l ON l.id_libro = e.id_libro
        JOIN sedes origen ON origen.id_sede = sp.id_sede_origen
        JOIN sedes destino ON destino.id_sede = sp.id_sede_destino
        ORDER BY sp.id_solicitud DESC
    """)

    solicitudes = cursor.fetchall()
    conexion.close()
    return solicitudes


def consultar_ejemplares_solicitables():
    """Solo copias disponibles en origen y sin reservas pendientes anteriores."""
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT e.id_ejemplar, e.codigo, l.titulo, l.isbn,
               s.nombre, e.estado, e.id_libro, e.id_sede
        FROM ejemplares e
        JOIN libros l ON l.id_libro = e.id_libro
        JOIN sedes s ON s.id_sede = e.id_sede
        WHERE e.estado = 'Disponible'
          AND s.activa = 1
          AND COALESCE(e.id_sede_actual, e.id_sede) = e.id_sede
          AND NOT EXISTS (
              SELECT 1 FROM reservas r
              WHERE r.id_libro = e.id_libro
                AND r.id_sede = e.id_sede
                AND r.estado = 'Pendiente'
          )
        ORDER BY l.titulo, e.codigo
    """)

    ejemplares = cursor.fetchall()
    conexion.close()
    return ejemplares


def guardar_solicitud(solicitud):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        # Comprobar todo al modificar: un selector anterior puede haber quedado desactualizado.
        # Si hay reservas pendientes para el título y origen, tienen prioridad.
        # La copia tiene que estar físicamente en su sede propietaria.
        # El socio y las dos sedes deben estar habilitados.
        cursor.execute("""
            UPDATE ejemplares
            SET estado = 'Solicitado'
            WHERE id_ejemplar = ?
              AND id_sede = ?
              AND estado = 'Disponible'
              AND COALESCE(id_sede_actual, id_sede) = ?
              AND NOT EXISTS (
                  SELECT 1 FROM reservas r
                  WHERE r.id_libro = ejemplares.id_libro
                    AND r.id_sede = ejemplares.id_sede
                    AND r.estado = 'Pendiente'
              )
              AND EXISTS (
                  SELECT 1 FROM sedes
                  WHERE id_sede = ? AND activa = 1
              )
              AND EXISTS (
                  SELECT 1 FROM sedes
                  WHERE id_sede = ? AND activa = 1
              )
              AND EXISTS (
                  SELECT 1 FROM socios
                  WHERE id_socio = ? AND habilitado = 1
              )
        """, (
            solicitud.id_ejemplar,
            solicitud.id_sede_origen,
            solicitud.id_sede_origen,
            solicitud.id_sede_origen,
            solicitud.id_sede_destino,
            solicitud.id_socio
        ))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se puede solicitar este ejemplar: puede estar ocupado, "
                "fuera de su sede, reservado por otro socio, o la sede/socio "
                "puede estar inhabilitado"
            )

        cursor.execute("""
            INSERT INTO solicitudes_prestamo
            (id_socio, id_ejemplar, id_sede_origen,
             id_sede_destino, tipo, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            solicitud.id_socio,
            solicitud.id_ejemplar,
            solicitud.id_sede_origen,
            solicitud.id_sede_destino,
            solicitud.tipo,
            solicitud.estado
        ))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def cancelar_solicitud(id_solicitud):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT id_ejemplar, estado
            FROM solicitudes_prestamo
            WHERE id_solicitud = ?
        """, (id_solicitud,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("La solicitud no existe")

        if datos[1] not in ("Pendiente", "Pendiente de traslado"):
            raise ValueError("Esta solicitud ya no puede cancelarse")

        cursor.execute("""
            UPDATE ejemplares
            SET estado = 'Disponible'
            WHERE id_ejemplar = ? AND estado = 'Solicitado'
        """, (datos[0],))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo liberar el ejemplar de la solicitud"
            )

        cursor.execute("""
            UPDATE solicitudes_prestamo
            SET estado = 'Cancelada'
            WHERE id_solicitud = ? AND estado IN ('Pendiente', 'Pendiente de traslado')
        """, (id_solicitud,))

        if cursor.rowcount != 1:
            raise ValueError("No se pudo cancelar la solicitud")

        # Si la solicitud nació de una reserva, devolver esa reserva a la cola.
        cursor.execute("""
            UPDATE reservas
            SET estado = 'Pendiente', id_solicitud = NULL
            WHERE id_solicitud = ? AND estado = 'Atendida'
        """, (id_solicitud,))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
