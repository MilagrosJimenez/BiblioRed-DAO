
import sqlite3

from datos.base_datos import RUTA_BASE_DATOS


def crear_tabla_reservas():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
            id_socio INTEGER NOT NULL,
            id_libro INTEGER NOT NULL,
            id_sede INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            fecha_reserva TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            id_solicitud INTEGER,
            FOREIGN KEY (id_socio) REFERENCES socios(id_socio),
            FOREIGN KEY (id_libro) REFERENCES libros(id_libro),
            FOREIGN KEY (id_sede) REFERENCES sedes(id_sede),
            FOREIGN KEY (id_solicitud) REFERENCES solicitudes_prestamo(id_solicitud)
        )
    """)

    conexion.commit()
    conexion.close()


def consultar_disponibilidad():
    """Existencias físicas y ejemplares realmente solicitables en cada sede."""
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT l.id_libro, l.titulo, l.isbn,
               s.id_sede, s.nombre,
               COUNT(e.id_ejemplar) AS copias_en_sede,
               COALESCE(SUM(
                   CASE WHEN e.estado = 'Disponible'
                             AND e.id_sede = s.id_sede
                             AND NOT EXISTS (
                                 SELECT 1 FROM reservas r
                                 WHERE r.id_libro = l.id_libro
                                   AND r.id_sede = s.id_sede
                                   AND r.estado = 'Pendiente'
                             )
                        THEN 1 ELSE 0 END
               ), 0) AS disponibles,
               (SELECT COUNT(*) FROM reservas r
                WHERE r.id_libro = l.id_libro
                  AND r.id_sede = s.id_sede
                  AND r.estado = 'Pendiente') AS reservas_pendientes

        FROM libros l
        CROSS JOIN sedes s

        LEFT JOIN ejemplares e
          ON e.id_libro = l.id_libro
         AND COALESCE(e.id_sede_actual, e.id_sede) = s.id_sede
         AND e.estado NOT IN ('Prestado', 'En tránsito', 'Retorno en tránsito')

        WHERE s.activa = 1

        GROUP BY l.id_libro, l.titulo, l.isbn, s.id_sede, s.nombre
        ORDER BY l.titulo, s.nombre
    """)

    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def consultar_reservas():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT r.id_reserva,
               so.apellido || ', ' || so.nombre,
               so.documento,
               l.titulo,
               s.nombre,
               r.estado,
               r.fecha_reserva,
               r.id_solicitud

        FROM reservas r

        JOIN socios so ON r.id_socio = so.id_socio
        JOIN libros l ON r.id_libro = l.id_libro
        JOIN sedes s ON r.id_sede = s.id_sede

        ORDER BY r.id_reserva DESC
    """)

    resultados = cursor.fetchall()
    conexion.close()

    return resultados


def guardar_reserva(reserva):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute(
            "SELECT habilitado FROM socios WHERE id_socio = ?",
            (reserva.id_socio,)
        )

        socio = cursor.fetchone()

        if socio is None or socio[0] != 1:
            raise ValueError(
                "El socio no existe o está inhabilitado"
            )

        cursor.execute(
            "SELECT activa FROM sedes WHERE id_sede = ?",
            (reserva.id_sede,)
        )

        sede = cursor.fetchone()

        if sede is None or sede[0] != 1:
            raise ValueError(
                "La sede no existe o está dada de baja"
            )

        cursor.execute(
            "SELECT id_libro FROM libros WHERE id_libro = ?",
            (reserva.id_libro,)
        )

        if cursor.fetchone() is None:
            raise ValueError(
                "El título seleccionado no existe"
            )

        cursor.execute("""
            SELECT id_reserva FROM reservas
            WHERE id_socio = ?
              AND id_libro = ?
              AND id_sede = ?
              AND (
                  estado = 'Pendiente'
                  OR (
                      estado = 'Atendida'
                      AND EXISTS (
                          SELECT 1 FROM solicitudes_prestamo sp
                          WHERE sp.id_solicitud = reservas.id_solicitud
                            AND sp.estado NOT IN ('Cancelada', 'Prestada')
                      )
                  )
              )
        """, (
            reserva.id_socio,
            reserva.id_libro,
            reserva.id_sede
        ))

        if cursor.fetchone() is not None:
            raise ValueError(
                "El socio ya tiene una reserva o una solicitud activa "
                "de este título en esa sede"
            )

        cursor.execute("""
            INSERT INTO reservas
            (id_socio, id_libro, id_sede, estado)
            VALUES (?, ?, ?, ?)
        """, (
            reserva.id_socio,
            reserva.id_libro,
            reserva.id_sede,
            reserva.estado
        ))

        nueva_id = cursor.lastrowid

        conexion.commit()
        return nueva_id

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def cancelar_reserva(id_reserva):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            UPDATE reservas
            SET estado = 'Cancelada'
            WHERE id_reserva = ?
              AND estado = 'Pendiente'
        """, (id_reserva,))

        if cursor.rowcount != 1:
            raise ValueError(
                "La reserva no existe o ya no está pendiente"
            )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def atender_reserva(id_reserva):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT r.id_socio, r.id_libro, r.id_sede,
                   r.estado, so.habilitado, s.activa

            FROM reservas r

            JOIN socios so ON so.id_socio = r.id_socio
            JOIN sedes s ON s.id_sede = r.id_sede

            WHERE r.id_reserva = ?
        """, (id_reserva,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("La reserva no existe")

        id_socio, id_libro, id_sede, estado, habilitado, activa = datos

        if estado != "Pendiente":
            raise ValueError(
                "Solo se pueden atender reservas pendientes"
            )

        if habilitado != 1 or activa != 1:
            raise ValueError(
                "El socio y la sede deben estar habilitados"
            )

        # Respetar el orden de las reservas pendientes
        cursor.execute("""
            SELECT MIN(id_reserva)
            FROM reservas
            WHERE id_libro = ?
              AND id_sede = ?
              AND estado = 'Pendiente'
        """, (id_libro, id_sede))

        if cursor.fetchone()[0] != id_reserva:
            raise ValueError(
                "Hay otra reserva anterior para este título y sede"
            )

        # Buscar una copia disponible en la sede
        cursor.execute("""
            SELECT id_ejemplar
            FROM ejemplares

            WHERE id_libro = ?
              AND id_sede = ?
              AND COALESCE(id_sede_actual, id_sede) = ?
              AND estado = 'Disponible'

            ORDER BY id_ejemplar
            LIMIT 1
        """, (id_libro, id_sede, id_sede))

        ejemplar = cursor.fetchone()

        if ejemplar is None:
            raise ValueError(
                "Todavía no hay ejemplares disponibles en esa sede"
            )

        id_ejemplar = ejemplar[0]

        cursor.execute("""
            UPDATE ejemplares
            SET estado = 'Solicitado'
            WHERE id_ejemplar = ?
              AND estado = 'Disponible'
        """, (id_ejemplar,))

        if cursor.rowcount != 1:
            raise ValueError(
                "El ejemplar dejó de estar disponible"
            )

        # Crear una solicitud local para el socio
        cursor.execute("""
            INSERT INTO solicitudes_prestamo
            (id_socio, id_ejemplar, id_sede_origen,
             id_sede_destino, tipo, estado)

            VALUES (?, ?, ?, ?, 'Local', 'Pendiente')
        """, (
            id_socio,
            id_ejemplar,
            id_sede,
            id_sede
        ))

        id_solicitud = cursor.lastrowid

        cursor.execute("""
            UPDATE reservas
            SET estado = 'Atendida',
                id_solicitud = ?
            WHERE id_reserva = ?
              AND estado = 'Pendiente'
        """, (id_solicitud, id_reserva))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar la reserva"
            )

        conexion.commit()
        return id_solicitud

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
