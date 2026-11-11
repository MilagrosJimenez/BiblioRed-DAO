
import sqlite3

from datos.base_datos import RUTA_BASE_DATOS
from clases.remito import Remito
from clases.tipos import TipoRemito
from datos.remito_modelo import cargar_remito


def crear_tablas_remitos(ruta=None):
    conexion = sqlite3.connect(ruta or RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    # Agregar ubicación física a los ejemplares existentes
    cursor.execute("PRAGMA table_info(ejemplares)")
    columnas = [fila[1] for fila in cursor.fetchall()]

    if "id_sede_actual" not in columnas:
        cursor.execute("""
            ALTER TABLE ejemplares
            ADD COLUMN id_sede_actual INTEGER
        """)

    cursor.execute("""
        UPDATE ejemplares
        SET id_sede_actual = id_sede
        WHERE id_sede_actual IS NULL
    """)

    # id_sede_actual nació como columna agregada a una tabla existente.
    # SQLite no permite agregarle FK con ALTER TABLE; estos disparadores
    # validan su referencia sin reconstruir ni poner en riesgo el catálogo.
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS ubicacion_valida_insert
        BEFORE INSERT ON ejemplares
        WHEN NEW.id_sede_actual IS NOT NULL
             AND NOT EXISTS (
                 SELECT 1 FROM sedes
                 WHERE id_sede = NEW.id_sede_actual
             )
        BEGIN
            SELECT RAISE(ABORT, 'La sede actual no existe');
        END
    """)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS ubicacion_valida_update
        BEFORE UPDATE OF id_sede_actual ON ejemplares
        WHEN NEW.id_sede_actual IS NOT NULL
             AND NOT EXISTS (
                 SELECT 1 FROM sedes
                 WHERE id_sede = NEW.id_sede_actual
             )
        BEGIN
            SELECT RAISE(ABORT, 'La sede actual no existe');
        END
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remitos (
            id_remito INTEGER PRIMARY KEY AUTOINCREMENT,
            id_solicitud INTEGER NOT NULL UNIQUE,
            id_ejemplar INTEGER NOT NULL,
            id_sede_origen INTEGER NOT NULL,
            id_sede_destino INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL
                DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (id_solicitud)
                REFERENCES solicitudes_prestamo(id_solicitud),

            FOREIGN KEY (id_ejemplar)
                REFERENCES ejemplares(id_ejemplar),

            FOREIGN KEY (id_sede_origen)
                REFERENCES sedes(id_sede),

            FOREIGN KEY (id_sede_destino)
                REFERENCES sedes(id_sede)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_remitos (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            id_remito INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL
                DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (id_remito)
                REFERENCES remitos(id_remito)
        )
    """)

    # Migración segura: agregar observaciones sin perder historiales anteriores.
    cursor.execute("PRAGMA table_info(historial_remitos)")
    if "observacion" not in [fila[1] for fila in cursor.fetchall()]:
        cursor.execute("""
            ALTER TABLE historial_remitos
            ADD COLUMN observacion TEXT NOT NULL DEFAULT ''
        """)

    conexion.commit()
    conexion.close()


def consultar_pendientes_traslado():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT sp.id_solicitud,
               e.codigo,
               l.titulo,
               origen.nombre,
               destino.nombre,
               sp.id_ejemplar,
               sp.id_sede_origen,
               sp.id_sede_destino

        FROM solicitudes_prestamo sp

        JOIN ejemplares e
            ON sp.id_ejemplar = e.id_ejemplar

        JOIN libros l
            ON e.id_libro = l.id_libro

        JOIN sedes origen
            ON origen.id_sede = sp.id_sede_origen

        JOIN sedes destino
            ON destino.id_sede = sp.id_sede_destino

        WHERE sp.tipo = 'Interbibliotecario'
          AND sp.estado = 'Pendiente de traslado'
          AND e.estado = 'Solicitado'
          AND origen.activa = 1
          AND destino.activa = 1
          AND NOT EXISTS (
              SELECT 1
              FROM remitos r
              WHERE r.id_solicitud = sp.id_solicitud
          )

        ORDER BY sp.id_solicitud
    """)

    pendientes = cursor.fetchall()
    conexion.close()

    return pendientes


def consultar_remitos():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT r.id_remito,
               e.codigo,
               l.titulo,
               origen.nombre,
               destino.nombre,
               r.estado,
               r.fecha_creacion,
               r.id_solicitud,
               r.id_ejemplar,
               r.id_sede_origen,
               r.id_sede_destino

        FROM remitos r

        JOIN ejemplares e
            ON r.id_ejemplar = e.id_ejemplar

        JOIN libros l
            ON e.id_libro = l.id_libro

        JOIN sedes origen
            ON r.id_sede_origen = origen.id_sede

        JOIN sedes destino
            ON r.id_sede_destino = destino.id_sede

        ORDER BY r.id_remito DESC
    """)

    remitos = cursor.fetchall()
    conexion.close()

    return remitos


def consultar_historial_remito(id_remito):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT estado, fecha, observacion
        FROM historial_remitos
        WHERE id_remito = ?
        ORDER BY id_historial
    """, (id_remito,))

    historial = cursor.fetchall()
    conexion.close()

    return historial


def empaquetar_solicitud(id_solicitud):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT sp.id_ejemplar,
                   sp.id_sede_origen,
                   sp.id_sede_destino,
                   sp.estado,
                   sp.tipo,
                   e.estado,
                   e.id_sede,
                   e.id_sede_actual,
                   origen.activa,
                   destino.activa

            FROM solicitudes_prestamo sp

            JOIN ejemplares e
                ON e.id_ejemplar = sp.id_ejemplar

            JOIN sedes origen
                ON origen.id_sede = sp.id_sede_origen

            JOIN sedes destino
                ON destino.id_sede = sp.id_sede_destino

            WHERE sp.id_solicitud = ?
        """, (id_solicitud,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("La solicitud no existe")

        (
            ejemplar, origen, destino, estado_sol, tipo,
            estado_ej, sede_duena, sede_actual,
            activa_o, activa_d
        ) = datos

        if (
            tipo != "Interbibliotecario"
            or origen == destino
            or estado_sol != "Pendiente de traslado"
        ):
            raise ValueError(
                "La solicitud no está pendiente de traslado "
                "interbibliotecario"
            )

        if (
            estado_ej != "Solicitado"
            or sede_duena != origen
            or sede_actual != origen
        ):
            raise ValueError(
                "El ejemplar no está disponible para "
                "empaquetar en su sede de origen"
            )

        if activa_o != 1 or activa_d != 1:
            raise ValueError("Ambas sedes deben estar activas")

        remito = Remito(id_solicitud, ejemplar, origen, destino)

        cursor.execute("""
            UPDATE solicitudes_prestamo
            SET estado = 'Empaquetada'
            WHERE id_solicitud = ?
              AND estado = 'Pendiente de traslado'
        """, (id_solicitud,))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo cambiar el estado de la solicitud"
            )

        cursor.execute("""
            UPDATE ejemplares
            SET estado = 'Empaquetado'
            WHERE id_ejemplar = ?
              AND estado = 'Solicitado'
        """, (ejemplar,))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo preparar el ejemplar"
            )

        cursor.execute("""
            INSERT INTO remitos
            (id_solicitud, id_ejemplar,
             id_sede_origen, id_sede_destino, estado)

            VALUES (?, ?, ?, ?, 'Empaquetado')
        """, (
            id_solicitud,
            ejemplar,
            origen,
            destino
        ))

        id_remito = cursor.lastrowid

        cursor.execute("""
            INSERT INTO historial_remitos
            (id_remito, estado, fecha, observacion)
            VALUES (?, ?, ?, 'Ejemplar preparado para despacho')
        """, (id_remito, remito.estado,
              remito.historial_movimientos[-1].fecha_hora.isoformat(sep=" ")))

        conexion.commit()

        return id_remito

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def avanzar_remito(id_remito, nuevo_estado):
    estados = {
        "En tránsito": (
            "Empaquetado",
            "Empaquetada",
            "Empaquetado",
            "En tránsito"
        ),
        "Recibido": (
            "En tránsito",
            "En tránsito",
            "En tránsito",
            "Recibida en destino"
        )
    }

    if nuevo_estado not in estados:
        raise ValueError("Estado de remito no permitido")

    (
        estado_anterior,
        solicitud_anterior,
        ejemplar_anterior,
        solicitud_nueva
    ) = estados[nuevo_estado]

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT r.id_solicitud,
                   r.id_ejemplar,
                   r.id_sede_destino,
                   r.estado,
                   sp.estado,
                   e.estado,
                   destino.activa,
                    origen.activa

            FROM remitos r

            JOIN solicitudes_prestamo sp
                ON sp.id_solicitud = r.id_solicitud

            JOIN ejemplares e
                ON e.id_ejemplar = r.id_ejemplar

            JOIN sedes destino
                ON destino.id_sede = r.id_sede_destino

            JOIN sedes origen
                ON origen.id_sede = r.id_sede_origen

            WHERE r.id_remito = ?
        """, (id_remito,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("El remito no existe")

        (
            id_solicitud,
            id_ejemplar,
            id_destino,
            actual_remito,
            actual_solicitud,
            actual_ejemplar,
            destino_activa,
            origen_activa
        ) = datos

        remito = cargar_remito(cursor, id_remito, TipoRemito.IDA)
        observacion = ("Ejemplar despachado" if nuevo_estado == "En tránsito"
                       else "Ejemplar recibido en destino")
        if nuevo_estado == "En tránsito":
            remito.despachar(observacion=observacion)
        else:
            remito.recibir(observacion=observacion)

        if (
            actual_remito != estado_anterior
            or actual_solicitud != solicitud_anterior
            or actual_ejemplar != ejemplar_anterior
        ):
            raise ValueError(
                "No se puede realizar esa operación "
                "desde el estado actual"
            )

        if destino_activa != 1:
            raise ValueError(
                "La sede destino debe estar activa"
            )

        if nuevo_estado == "En tránsito" and origen_activa != 1:
            raise ValueError(
                "No se puede despachar desde una sede dada de baja"
            )

        cursor.execute("""
            UPDATE remitos
            SET estado = ?
            WHERE id_remito = ? AND estado = ?
        """, (
            nuevo_estado,
            id_remito,
            estado_anterior
        ))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar el remito"
            )

        cursor.execute("""
            UPDATE solicitudes_prestamo
            SET estado = ?
            WHERE id_solicitud = ? AND estado = ?
        """, (
            solicitud_nueva,
            id_solicitud,
            solicitud_anterior
        ))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar la solicitud"
            )

        if nuevo_estado == "Recibido":
            cursor.execute("""
                UPDATE ejemplares
                SET estado = 'Recibido',
                    id_sede_actual = ?
                WHERE id_ejemplar = ?
                  AND estado = 'En tránsito'
            """, (
                id_destino,
                id_ejemplar
            ))

        else:
            cursor.execute("""
                UPDATE ejemplares
                SET estado = 'En tránsito'
                WHERE id_ejemplar = ?
                  AND estado = 'Empaquetado'
            """, (id_ejemplar,))

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar el estado del ejemplar"
            )

        cursor.execute("""
            INSERT INTO historial_remitos
            (id_remito, estado, fecha, observacion)
            VALUES (?, ?, ?, ?)
        """, (
            id_remito,
            remito.estado,
            remito.historial_movimientos[-1].fecha_hora.isoformat(sep=" "),
            remito.historial_movimientos[-1].observacion
        ))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
