
import sqlite3

from datos.base_datos import RUTA_BASE_DATOS
from clases.solicitud_prestamo import SolicitudPrestamo


def crear_tabla_prestamos():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id_prestamo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_solicitud INTEGER NOT NULL UNIQUE,
            id_socio INTEGER NOT NULL,
            id_ejemplar INTEGER NOT NULL,
            fecha_prestamo TEXT NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            fecha_devolucion TEXT,
            estado TEXT NOT NULL,

            FOREIGN KEY (id_solicitud)
                REFERENCES solicitudes_prestamo(id_solicitud),

            FOREIGN KEY (id_socio)
                REFERENCES socios(id_socio),

            FOREIGN KEY (id_ejemplar)
                REFERENCES ejemplares(id_ejemplar)
        )
    """)

    conexion.commit()
    conexion.close()


def consultar_solicitudes_para_entrega():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT sp.id_solicitud,
               s.apellido || ', ' || s.nombre,
               e.codigo,
               l.titulo,
               destino.nombre,
               sp.tipo

        FROM solicitudes_prestamo sp

        JOIN socios s
            ON s.id_socio = sp.id_socio

        JOIN ejemplares e
            ON e.id_ejemplar = sp.id_ejemplar

        JOIN libros l
            ON l.id_libro = e.id_libro

        JOIN sedes origen
            ON origen.id_sede = sp.id_sede_origen

        JOIN sedes destino
            ON destino.id_sede = sp.id_sede_destino

        WHERE s.habilitado = 1
          AND origen.activa = 1
          AND destino.activa = 1
          AND e.id_sede = sp.id_sede_origen

          AND NOT EXISTS (
              SELECT 1
              FROM prestamos p
              WHERE p.id_solicitud = sp.id_solicitud
                 OR (
                     p.id_ejemplar = sp.id_ejemplar
                     AND p.estado = 'Activo'
                 )
          )

          AND (
              (
                  sp.tipo = 'Local'
                  AND sp.estado = 'Pendiente'
                  AND sp.id_sede_origen = sp.id_sede_destino
                  AND e.estado = 'Solicitado'
                  AND COALESCE(e.id_sede_actual, e.id_sede)
                      = sp.id_sede_origen
              )

              OR

              (
                  sp.tipo = 'Interbibliotecario'
                  AND sp.estado = 'Recibida en destino'
                  AND sp.id_sede_origen != sp.id_sede_destino
                  AND e.estado = 'Recibido'
                  AND e.id_sede_actual = sp.id_sede_destino

                  AND EXISTS (
                      SELECT 1
                      FROM remitos r
                      WHERE r.id_solicitud = sp.id_solicitud
                        AND r.estado = 'Recibido'
                  )
              )
          )

        ORDER BY sp.id_solicitud
    """)

    resultados = cursor.fetchall()
    conexion.close()

    return resultados


def consultar_prestamos():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT p.id_prestamo,
               s.apellido || ', ' || s.nombre,
               s.documento,
               e.codigo,
               l.titulo,
               destino.nombre,
               p.fecha_prestamo,
               p.fecha_vencimiento,
               p.estado,
               sp.tipo

        FROM prestamos p

        JOIN solicitudes_prestamo sp
            ON sp.id_solicitud = p.id_solicitud

        JOIN socios s
            ON s.id_socio = p.id_socio

        JOIN ejemplares e
            ON e.id_ejemplar = p.id_ejemplar

        JOIN libros l
            ON l.id_libro = e.id_libro

        JOIN sedes destino
            ON destino.id_sede = sp.id_sede_destino

        ORDER BY p.id_prestamo DESC
    """)

    resultados = cursor.fetchall()
    conexion.close()

    return resultados


def registrar_prestamo(prestamo):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT sp.id_socio,
                   sp.id_ejemplar,
                   sp.tipo,
                   sp.estado,
                   sp.id_sede_origen,
                   sp.id_sede_destino,
                   s.habilitado,
                   origen.activa,
                   destino.activa,
                   e.estado,
                   e.id_sede,
                   e.id_sede_actual

            FROM solicitudes_prestamo sp

            JOIN socios s
                ON s.id_socio = sp.id_socio

            JOIN ejemplares e
                ON e.id_ejemplar = sp.id_ejemplar

            JOIN sedes origen
                ON origen.id_sede = sp.id_sede_origen

            JOIN sedes destino
                ON destino.id_sede = sp.id_sede_destino

            WHERE sp.id_solicitud = ?
        """, (prestamo.id_solicitud,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("La solicitud no existe")

        (
            id_socio,
            id_ejemplar,
            tipo,
            estado_solicitud,
            id_origen,
            id_destino,
            socio_habilitado,
            origen_activa,
            destino_activa,
            estado_ejemplar,
            sede_propietaria,
            sede_actual
        ) = datos

        # Validar socio y sedes
        if socio_habilitado != 1:
            raise ValueError("El socio está inhabilitado")

        if origen_activa != 1 or destino_activa != 1:
            raise ValueError(
                "La sede de origen o destino está dada de baja"
            )

        if sede_propietaria != id_origen:
            raise ValueError(
                "El ejemplar no pertenece a la sede de origen"
            )

        # Préstamo local
        if tipo == "Local":

            if (
                id_origen != id_destino
                or estado_solicitud != "Pendiente"
                or estado_ejemplar != "Solicitado"
                or (sede_actual or sede_propietaria) != id_origen
            ):
                raise ValueError(
                    "La solicitud local no está lista para entregar"
                )

        # Préstamo interbibliotecario
        elif tipo == "Interbibliotecario":

            if (
                id_origen == id_destino
                or estado_solicitud != "Recibida en destino"
                or estado_ejemplar != "Recibido"
                or sede_actual != id_destino
            ):
                raise ValueError(
                    "El traslado todavía no fue recibido en destino"
                )

            cursor.execute("""
                SELECT estado
                FROM remitos
                WHERE id_solicitud = ?
            """, (prestamo.id_solicitud,))

            remito = cursor.fetchone()

            if remito is None or remito[0] != "Recibido":
                raise ValueError(
                    "El remito debe estar recibido antes del préstamo"
                )

        else:
            raise ValueError("Tipo de solicitud desconocido")

        # Evitar préstamos duplicados
        cursor.execute("""
            SELECT id_prestamo
            FROM prestamos
            WHERE id_solicitud = ?
               OR (
                   id_ejemplar = ?
                   AND estado = 'Activo'
               )
        """, (
            prestamo.id_solicitud,
            id_ejemplar
        ))

        if cursor.fetchone() is not None:
            raise ValueError(
                "Ya existe un préstamo para esta solicitud o ejemplar"
            )

        # La solicitud genera el préstamo y éste delega el vencimiento (UML).
        solicitud = SolicitudPrestamo(
            id_socio, id_ejemplar, id_origen, id_destino,
            id_solicitud=prestamo.id_solicitud, estado=estado_solicitud,
        )
        prestamo = solicitud.confirmar_entrega(
            estrategia_plazo=prestamo.estrategia_plazo,
            fecha_entrega=prestamo.fecha_entrega,
        )

        # Actualizar la solicitud
        cursor.execute("""
            UPDATE solicitudes_prestamo
            SET estado = 'Prestada'
            WHERE id_solicitud = ?
              AND estado = ?
        """, (
            prestamo.id_solicitud,
            estado_solicitud
        ))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar la solicitud"
            )

        # Actualizar el ejemplar
        cursor.execute("""
            UPDATE ejemplares
            SET estado = 'Prestado'
            WHERE id_ejemplar = ?
              AND estado = ?
        """, (
            id_ejemplar,
            estado_ejemplar
        ))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar el ejemplar"
            )

        # Registrar préstamo
        cursor.execute("""
            INSERT INTO prestamos (
                id_solicitud,
                id_socio,
                id_ejemplar,
                fecha_prestamo,
                fecha_vencimiento,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            prestamo.id_solicitud,
            id_socio,
            id_ejemplar,
            prestamo.fecha_prestamo,
            prestamo.fecha_vencimiento.isoformat(),
            prestamo.estado
        ))

        nuevo_id = cursor.lastrowid

        conexion.commit()

        return nuevo_id

    except sqlite3.IntegrityError as error:
        conexion.rollback()
        raise ValueError(
            "No se pudo registrar: préstamo duplicado o datos inválidos"
        ) from error

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
