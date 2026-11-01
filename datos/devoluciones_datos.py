
import sqlite3
from datos.base_datos import RUTA_BASE_DATOS


def crear_tablas_devoluciones():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devoluciones (
            id_devolucion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_prestamo INTEGER NOT NULL UNIQUE,
            id_ejemplar INTEGER NOT NULL,
            id_sede_recepcion INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            estado_fisico TEXT NOT NULL,
            observaciones TEXT NOT NULL,
            FOREIGN KEY (id_prestamo) REFERENCES prestamos(id_prestamo),
            FOREIGN KEY (id_ejemplar) REFERENCES ejemplares(id_ejemplar),
            FOREIGN KEY (id_sede_recepcion) REFERENCES sedes(id_sede)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remitos_retorno (
            id_remito INTEGER PRIMARY KEY AUTOINCREMENT,
            id_devolucion INTEGER NOT NULL UNIQUE,
            id_ejemplar INTEGER NOT NULL,
            id_sede_origen INTEGER NOT NULL,
            id_sede_destino INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (id_devolucion) REFERENCES devoluciones(id_devolucion),
            FOREIGN KEY (id_ejemplar) REFERENCES ejemplares(id_ejemplar),
            FOREIGN KEY (id_sede_origen) REFERENCES sedes(id_sede),
            FOREIGN KEY (id_sede_destino) REFERENCES sedes(id_sede)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_retornos (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            id_remito INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (id_remito) REFERENCES remitos_retorno(id_remito)
        )
    """)

    conexion.commit()
    conexion.close()


def consultar_prestamos_activos():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT p.id_prestamo, s.apellido || ', ' || s.nombre,
               e.codigo, l.titulo, sede.nombre, p.fecha_vencimiento,
               sp.tipo
        FROM prestamos p
        JOIN socios s ON p.id_socio = s.id_socio
        JOIN ejemplares e ON p.id_ejemplar = e.id_ejemplar
        JOIN libros l ON e.id_libro = l.id_libro
        JOIN solicitudes_prestamo sp ON p.id_solicitud = sp.id_solicitud
        JOIN sedes sede ON sp.id_sede_destino = sede.id_sede
        WHERE p.estado = 'Activo' AND e.estado = 'Prestado'
        ORDER BY p.id_prestamo
    """)

    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def consultar_devoluciones():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT d.id_devolucion, d.fecha, d.estado_fisico,
               d.observaciones, p.id_prestamo,
               s.apellido || ', ' || s.nombre,
               e.codigo, l.titulo, recepcion.nombre, sp.tipo,
               e.estado, propietaria.nombre
        FROM devoluciones d
        JOIN prestamos p ON d.id_prestamo = p.id_prestamo
        JOIN socios s ON p.id_socio = s.id_socio
        JOIN ejemplares e ON d.id_ejemplar = e.id_ejemplar
        JOIN libros l ON e.id_libro = l.id_libro
        JOIN sedes recepcion ON recepcion.id_sede = d.id_sede_recepcion
        JOIN sedes propietaria ON propietaria.id_sede = e.id_sede
        JOIN solicitudes_prestamo sp ON p.id_solicitud = sp.id_solicitud
        ORDER BY d.id_devolucion DESC
    """)

    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def registrar_devolucion(devolucion):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT p.id_ejemplar, p.estado, sp.tipo,
                   sp.id_sede_origen, sp.id_sede_destino,
                   e.estado, e.id_sede, e.id_sede_actual
            FROM prestamos p
            JOIN solicitudes_prestamo sp
                ON sp.id_solicitud = p.id_solicitud
            JOIN ejemplares e ON e.id_ejemplar = p.id_ejemplar
            WHERE p.id_prestamo = ?
        """, (devolucion.id_prestamo,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("El préstamo no existe")

        (id_ejemplar, estado_p, tipo, id_origen, id_destino,
         estado_e, sede_propietaria, sede_actual) = datos

        if estado_p != "Activo" or estado_e != "Prestado":
            raise ValueError(
                "El préstamo ya fue devuelto o no está activo"
            )

        if sede_propietaria != id_origen or sede_actual != id_destino:
            raise ValueError(
                "La ubicación del ejemplar no coincide con el préstamo"
            )

        if tipo == "Local" and id_origen == id_destino:
            estado_nuevo = (
                "Disponible" if devolucion.estado_fisico == "Bueno"
                else "En revisión"
            )

        elif tipo == "Interbibliotecario" and id_origen != id_destino:
            estado_nuevo = "Pendiente de retorno"

        else:
            raise ValueError("El tipo de préstamo no es válido")

        cursor.execute("""
            INSERT INTO devoluciones
            (id_prestamo, id_ejemplar, id_sede_recepcion,
             fecha, estado_fisico, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            devolucion.id_prestamo,
            id_ejemplar,
            id_destino,
            devolucion.fecha,
            devolucion.estado_fisico,
            devolucion.observaciones
        ))

        id_devolucion = cursor.lastrowid

        cursor.execute("""
            UPDATE prestamos
            SET estado = 'Devuelto', fecha_devolucion = ?
            WHERE id_prestamo = ? AND estado = 'Activo'
        """, (
            devolucion.fecha,
            devolucion.id_prestamo
        ))

        if cursor.rowcount != 1:
            raise ValueError("No se pudo cerrar el préstamo")

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?
            WHERE id_ejemplar = ? AND estado = 'Prestado'
        """, (
            estado_nuevo,
            id_ejemplar
        ))

        if cursor.rowcount != 1:
            raise ValueError("No se pudo actualizar el ejemplar")

        conexion.commit()
        return id_devolucion

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def consultar_pendientes_retorno():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT d.id_devolucion, e.codigo, l.titulo,
               actual.nombre, propietaria.nombre
        FROM devoluciones d
        JOIN ejemplares e ON d.id_ejemplar = e.id_ejemplar
        JOIN libros l ON e.id_libro = l.id_libro
        JOIN sedes actual ON d.id_sede_recepcion = actual.id_sede
        JOIN sedes propietaria ON e.id_sede = propietaria.id_sede
        JOIN prestamos p ON d.id_prestamo = p.id_prestamo
        JOIN solicitudes_prestamo sp ON p.id_solicitud = sp.id_solicitud
        WHERE sp.tipo = 'Interbibliotecario'
          AND e.estado = 'Pendiente de retorno'
          AND e.id_sede_actual = d.id_sede_recepcion
          AND d.id_sede_recepcion = sp.id_sede_destino
          AND e.id_sede = sp.id_sede_origen
          AND actual.activa = 1 AND propietaria.activa = 1
          AND NOT EXISTS (
              SELECT 1 FROM remitos_retorno r
              WHERE r.id_devolucion = d.id_devolucion
          )
        ORDER BY d.id_devolucion
    """)

    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def consultar_remitos_retorno():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT r.id_remito, r.id_devolucion, e.codigo,
               l.titulo, origen.nombre, destino.nombre,
               r.estado, d.estado_fisico
        FROM remitos_retorno r
        JOIN devoluciones d ON r.id_devolucion = d.id_devolucion
        JOIN ejemplares e ON r.id_ejemplar = e.id_ejemplar
        JOIN libros l ON e.id_libro = l.id_libro
        JOIN sedes origen ON r.id_sede_origen = origen.id_sede
        JOIN sedes destino ON r.id_sede_destino = destino.id_sede
        ORDER BY r.id_remito DESC
    """)

    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def consultar_historial_retorno(id_remito):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT estado, fecha
        FROM historial_retornos
        WHERE id_remito = ?
        ORDER BY id_historial
    """, (id_remito,))

    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def preparar_retorno(id_devolucion):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT d.id_ejemplar, d.id_sede_recepcion,
                   e.id_sede, e.id_sede_actual, e.estado,
                   sp.tipo, origen.activa, destino.activa
            FROM devoluciones d
            JOIN ejemplares e ON d.id_ejemplar = e.id_ejemplar
            JOIN prestamos p ON d.id_prestamo = p.id_prestamo
            JOIN solicitudes_prestamo sp
                ON p.id_solicitud = sp.id_solicitud
            JOIN sedes origen ON origen.id_sede = d.id_sede_recepcion
            JOIN sedes destino ON destino.id_sede = e.id_sede
            WHERE d.id_devolucion = ?
        """, (id_devolucion,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("La devolución no existe")

        (id_ejemplar, id_origen, id_destino, sede_actual,
         estado_e, tipo, origen_activa, destino_activa) = datos

        if tipo != "Interbibliotecario" or id_origen == id_destino:
            raise ValueError(
                "Esta devolución no necesita un remito de retorno"
            )

        if sede_actual != id_origen or estado_e != "Pendiente de retorno":
            raise ValueError(
                "El ejemplar no está pendiente de retorno"
            )

        if origen_activa != 1 or destino_activa != 1:
            raise ValueError(
                "No se pueden iniciar envíos con sedes dadas de baja"
            )

        cursor.execute("""
            UPDATE ejemplares
            SET estado = 'Retorno empaquetado'
            WHERE id_ejemplar = ? AND estado = 'Pendiente de retorno'
        """, (id_ejemplar,))

        if cursor.rowcount != 1:
            raise ValueError("No se pudo empaquetar el ejemplar")

        cursor.execute("""
            INSERT INTO remitos_retorno
            (id_devolucion, id_ejemplar,
             id_sede_origen, id_sede_destino, estado)
            VALUES (?, ?, ?, ?, 'Empaquetado')
        """, (
            id_devolucion,
            id_ejemplar,
            id_origen,
            id_destino
        ))

        id_remito = cursor.lastrowid

        cursor.execute("""
            INSERT INTO historial_retornos (id_remito, estado)
            VALUES (?, 'Empaquetado')
        """, (id_remito,))

        conexion.commit()
        return id_remito

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def avanzar_retorno(id_remito, nuevo_estado):
    if nuevo_estado not in ("En tránsito", "Recibido"):
        raise ValueError("Estado solicitado inválido")

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT r.id_ejemplar, r.id_sede_origen, r.id_sede_destino,
                   r.estado, e.estado, e.id_sede_actual, e.id_sede,
                   d.estado_fisico, origen.activa, destino.activa
            FROM remitos_retorno r
            JOIN ejemplares e ON r.id_ejemplar = e.id_ejemplar
            JOIN devoluciones d ON r.id_devolucion = d.id_devolucion
            JOIN sedes origen ON r.id_sede_origen = origen.id_sede
            JOIN sedes destino ON r.id_sede_destino = destino.id_sede
            WHERE r.id_remito = ?
        """, (id_remito,))

        datos = cursor.fetchone()

        if datos is None:
            raise ValueError("El remito de retorno no existe")

        (id_ejemplar, id_origen, id_destino, estado_r,
         estado_e, sede_actual, propietaria, fisico,
         origen_activa, destino_activa) = datos

        if propietaria != id_destino:
            raise ValueError(
                "La sede destino debe ser la propietaria"
            )

        if nuevo_estado == "En tránsito":
            if (
                estado_r != "Empaquetado"
                or estado_e != "Retorno empaquetado"
            ):
                raise ValueError(
                    "El retorno no está listo para despachar"
                )

            if sede_actual != id_origen:
                raise ValueError(
                    "El ejemplar no está en la sede de salida"
                )

            if origen_activa != 1 or destino_activa != 1:
                raise ValueError(
                    "No se puede despachar con sedes dadas de baja"
                )

            nuevo_estado_e = "Retorno en tránsito"
            nueva_sede_actual = sede_actual

        else:
            if (
                estado_r != "En tránsito"
                or estado_e != "Retorno en tránsito"
            ):
                raise ValueError(
                    "El retorno debe estar en tránsito"
                )

            nuevo_estado_e = (
                "Disponible" if fisico == "Bueno"
                else "En revisión"
            )
            nueva_sede_actual = id_destino

        cursor.execute("""
            UPDATE remitos_retorno
            SET estado = ?
            WHERE id_remito = ? AND estado = ?
        """, (nuevo_estado, id_remito, estado_r))

        if cursor.rowcount != 1:
            raise ValueError("No se pudo actualizar el remito")

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?, id_sede_actual = ?
            WHERE id_ejemplar = ? AND estado = ?
        """, (
            nuevo_estado_e,
            nueva_sede_actual,
            id_ejemplar,
            estado_e
        ))

        if cursor.rowcount != 1:
            raise ValueError("No se pudo actualizar el ejemplar")

        cursor.execute("""
            INSERT INTO historial_retornos (id_remito, estado)
            VALUES (?, ?)
        """, (id_remito, nuevo_estado))

        conexion.commit()
        return nuevo_estado_e

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
