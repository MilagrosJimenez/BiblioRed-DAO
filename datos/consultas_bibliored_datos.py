"""Consultas del alcance entregado: inventario, historial y cuatro reportes."""
import sqlite3
from datos.base_datos import RUTA_BASE_DATOS


def _consultar(sql, parametros=()):
    with sqlite3.connect(RUTA_BASE_DATOS) as conexion:
        return conexion.execute(sql, parametros).fetchall()


def consultar_inventario(codigo="", sede=None):
    """Código único, título, estado, propietaria y ubicación registrada."""
    sql = """
        SELECT e.codigo, l.titulo, e.estado,
               propietaria.nombre,
               COALESCE(actual.nombre, propietaria.nombre)
        FROM ejemplares e
        JOIN libros l ON l.id_libro = e.id_libro
        JOIN sedes propietaria ON propietaria.id_sede = e.id_sede
        LEFT JOIN sedes actual ON actual.id_sede = e.id_sede_actual
        WHERE LOWER(e.codigo) LIKE LOWER(?)
    """
    parametros = ["%" + codigo.strip() + "%"]
    if sede is not None:
        sql += " AND (e.id_sede = ? OR COALESCE(e.id_sede_actual, e.id_sede) = ?)"
        parametros.extend([sede, sede])
    sql += " ORDER BY l.titulo, e.codigo"
    return _consultar(sql, parametros)


def consultar_historial_lecturas(id_socio):
    """Historial completo desde préstamos efectivos, incluidos los devueltos."""
    return _consultar("""
        SELECT l.titulo, e.codigo, p.fecha_prestamo,
               p.fecha_vencimiento, p.fecha_devolucion, p.estado
        FROM prestamos p
        JOIN ejemplares e ON e.id_ejemplar = p.id_ejemplar
        JOIN libros l ON l.id_libro = e.id_libro
        WHERE p.id_socio = ?
        ORDER BY p.fecha_prestamo DESC, p.id_prestamo DESC
    """, (id_socio,))


def reporte_prestamos_por_sede():
    return _consultar("""
        SELECT s.nombre,
               COUNT(p.id_prestamo) AS activos,
               COALESCE(SUM(CASE WHEN date(p.fecha_vencimiento) < date('now')
                                  THEN 1 ELSE 0 END), 0) AS vencidos,
               COALESCE(MAX(CASE WHEN date(p.fecha_vencimiento) < date('now')
                         THEN CAST(julianday(date('now')) -
                                   julianday(date(p.fecha_vencimiento)) AS INTEGER)
                         ELSE 0 END), 0) AS max_dias_vencido
        FROM sedes s
        LEFT JOIN solicitudes_prestamo sp ON sp.id_sede_destino = s.id_sede
        LEFT JOIN prestamos p ON p.id_solicitud = sp.id_solicitud
                             AND p.estado = 'Activo'
        GROUP BY s.id_sede, s.nombre
        ORDER BY vencidos DESC, activos DESC, s.nombre
    """)


def reporte_libros_mas_solicitados():
    return _consultar("""
        SELECT l.titulo, l.isbn, COUNT(sp.id_solicitud) AS solicitudes
        FROM solicitudes_prestamo sp
        JOIN ejemplares e ON e.id_ejemplar = sp.id_ejemplar
        JOIN libros l ON l.id_libro = e.id_libro
        WHERE sp.tipo = 'Interbibliotecario'
          AND sp.estado != 'Cancelada'
        GROUP BY l.id_libro, l.titulo, l.isbn
        ORDER BY solicitudes DESC, l.titulo
    """)


def reporte_disponibilidad():
    """Copias asignadas y libres en sede propietaria, con cola de reservas."""
    return _consultar("""
        SELECT s.nombre, l.titulo,
               COUNT(e.id_ejemplar) AS ejemplares,
               COALESCE(SUM(
                   CASE WHEN e.estado = 'Disponible'
                         AND COALESCE(e.id_sede_actual, e.id_sede) = s.id_sede
                         THEN 1 ELSE 0 END
               ), 0) AS libres_fisicos,
               (SELECT COUNT(*) FROM reservas r
                WHERE r.id_libro = l.id_libro
                  AND r.id_sede = s.id_sede
                  AND r.estado = 'Pendiente') AS reservas
        FROM ejemplares e
        JOIN libros l ON l.id_libro = e.id_libro
        JOIN sedes s ON s.id_sede = e.id_sede
        GROUP BY s.id_sede, l.id_libro
        ORDER BY s.nombre, l.titulo
    """)


def reporte_movimientos():
    """Incluye idas y retornos, evitando duplicaciones por historial.

    Tránsito se calcula entre primer despacho y primera recepción.
    Una recepción aún pendiente no interviene en el promedio.
    """
    return _consultar("""
        WITH movimientos AS (
            SELECT 'Ida' tipo, r.id_remito, r.id_sede_origen origen,
                   r.id_sede_destino destino
            FROM remitos r
            UNION ALL
            SELECT 'Retorno' tipo, r.id_remito, r.id_sede_origen origen,
                   r.id_sede_destino destino
            FROM remitos_retorno r
        ),
        duraciones AS (
            SELECT 'Ida' tipo, r.id_remito,
                (julianday(
                    (SELECT MIN(h.fecha) FROM historial_remitos h
                     WHERE h.id_remito = r.id_remito AND h.estado = 'Recibido')
                ) - julianday(
                    (SELECT MIN(h.fecha) FROM historial_remitos h
                     WHERE h.id_remito = r.id_remito AND h.estado = 'En tránsito')
                )) * 24.0 horas
            FROM remitos r
            UNION ALL
            SELECT 'Retorno', r.id_remito,
                (julianday(
                    (SELECT MIN(h.fecha) FROM historial_retornos h
                     WHERE h.id_remito = r.id_remito AND h.estado = 'Recibido')
                ) - julianday(
                    (SELECT MIN(h.fecha) FROM historial_retornos h
                     WHERE h.id_remito = r.id_remito AND h.estado = 'En tránsito')
                )) * 24.0 horas
            FROM remitos_retorno r
        )
        SELECT origen.nombre, destino.nombre,
               COUNT(*) AS envios,
               COUNT(d.horas) AS recibidos,
               ROUND(AVG(CASE WHEN d.horas >= 0 THEN d.horas END), 2) AS promedio_horas
        FROM movimientos m
        JOIN sedes origen ON origen.id_sede = m.origen
        JOIN sedes destino ON destino.id_sede = m.destino
        LEFT JOIN duraciones d ON d.tipo = m.tipo AND d.id_remito = m.id_remito
        GROUP BY m.origen, m.destino
        ORDER BY envios DESC, origen.nombre, destino.nombre
    """)


REPORTES = {
    "prestamos": (
        "Préstamos activos y vencidos por sede",
        ("Sede", "Activos", "Vencidos", "Máx. días vencido"),
        reporte_prestamos_por_sede
    ),
    "solicitados": (
        "Libros más solicitados para préstamos interbibliotecarios",
        ("Título", "ISBN", "Solicitudes"),
        reporte_libros_mas_solicitados
    ),
    "disponibilidad": (
        "Disponibilidad de títulos y ejemplares por sede",
        ("Sede propietaria", "Título", "Copias", "Libres", "Reservas"),
        reporte_disponibilidad
    ),
    "movimientos": (
        "Movimientos de ejemplares entre sedes",
        ("Origen", "Destino", "Envíos", "Recibidos", "Prom. horas"),
        reporte_movimientos
    ),
}
