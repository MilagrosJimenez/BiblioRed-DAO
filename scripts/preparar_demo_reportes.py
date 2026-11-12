"""Prepara una base SQLite NUEVA y aislada para demostrar los cuatro reportes.

No modifica biblioteca.db ni reutiliza una base de salida existente.
Se crean historiales coherentes de solicitudes, préstamos, devoluciones,
remitos y retornos con fechas ficticias para fines académicos.
"""
import argparse
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from scripts.importar_demo import importar_demo


def preparar(ruta: Path):
    ruta = ruta.resolve()
    if ruta.exists():
        raise FileExistsError(f"La base ya existe y no se modificará: {ruta}")
    try:
        importar_demo(ruta)
        con = sqlite3.connect(ruta)
        con.execute("PRAGMA foreign_keys = ON")
        hoy = date.today()
        socios = [f[0] for f in con.execute(
            "SELECT id_socio FROM socios WHERE habilitado = 1 ORDER BY id_socio"
        )]
        ejemplares = con.execute(
            "SELECT id_ejemplar,id_sede FROM ejemplares ORDER BY id_ejemplar"
        ).fetchall()
        sedes = [f[0] for f in con.execute(
            "SELECT id_sede FROM sedes ORDER BY id_sede"
        )]
        if not socios or len(ejemplares) < 18 or len(sedes) < 2:
            raise ValueError("No hay suficientes datos de demostración")
        with con:
            for i, (id_ejemplar, origen) in enumerate(ejemplares[:18]):
                # Alternar operaciones locales / entre sedes y activas / devueltas.
                inter = i % 3 != 0
                devuelto = i % 4 == 0 or i % 5 == 0
                destino = sedes[(sedes.index(origen) + 1) % len(sedes)] if inter else origen
                entrega = hoy - timedelta(days=6 + i * 4)
                vencimiento = entrega + timedelta(days=(7, 14, 21)[i % 3])
                solicitud_fecha = entrega - timedelta(days=3 if inter else 1)
                con.execute(
                    """INSERT INTO solicitudes_prestamo
                    (id_socio,id_ejemplar,id_sede_origen,id_sede_destino,tipo,estado,fecha_solicitud)
                    VALUES (?,?,?,?,?,'Prestada',?)""",
                    (socios[i % len(socios)],id_ejemplar,origen,destino,
                     "Interbibliotecario" if inter else "Local",solicitud_fecha.isoformat()))
                solicitud_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                if inter:
                    empaquetado = datetime.combine(entrega - timedelta(days=2), datetime.min.time()).replace(hour=9)
                    despacho = empaquetado + timedelta(hours=2)
                    recibido = despacho + timedelta(hours=4 + i % 6)
                    con.execute(
                        """INSERT INTO remitos
                        (id_solicitud,id_ejemplar,id_sede_origen,id_sede_destino,estado,fecha_creacion)
                        VALUES (?,?,?,?, 'Recibido',?)""",
                        (solicitud_id,id_ejemplar,origen,destino,empaquetado.isoformat(sep=" ")))
                    remito_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                    for estado,fecha in [("Empaquetado",empaquetado),("En tránsito",despacho),("Recibido",recibido)]:
                        con.execute("INSERT INTO historial_remitos (id_remito,estado,fecha,observacion) VALUES (?,?,?,?)",
                                    (remito_id,estado,fecha.isoformat(sep=" "),"Movimiento de demostración"))
                con.execute(
                    """INSERT INTO prestamos
                    (id_solicitud,id_socio,id_ejemplar,fecha_prestamo,fecha_vencimiento,fecha_devolucion,estado)
                    VALUES (?,?,?,?,?,?,?)""",
                    (solicitud_id,socios[i % len(socios)],id_ejemplar,
                     entrega.isoformat(),vencimiento.isoformat(),
                     (entrega + timedelta(days=4)).isoformat() if devuelto else None,
                     "Devuelto" if devuelto else "Activo"))
                prestamo_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                if devuelto:
                    fecha_dev = entrega + timedelta(days=4)
                    con.execute(
                        """INSERT INTO devoluciones
                        (id_prestamo,id_ejemplar,id_sede_recepcion,fecha,estado_fisico,observaciones)
                        VALUES (?,?,?,?,'Bueno','Devolución de demostración')""",
                        (prestamo_id,id_ejemplar,destino,fecha_dev.isoformat()))
                    id_devolucion = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                    if inter:
                        con.execute(
                            """INSERT INTO remitos_retorno
                            (id_devolucion,id_ejemplar,id_sede_origen,id_sede_destino,estado)
                            VALUES (?,?,?,?,'Recibido')""",
                            (id_devolucion,id_ejemplar,destino,origen))
                        retorno_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                        for estado,horas in [("Empaquetado",1),("En tránsito",2),("Recibido",9)]:
                            momento = datetime.combine(fecha_dev,datetime.min.time()).replace(hour=8) + timedelta(hours=horas)
                            con.execute("INSERT INTO historial_retornos (id_remito,estado,fecha,observacion) VALUES (?,?,?,?)",
                                        (retorno_id,estado,momento.isoformat(sep=" "),"Retorno de demostración"))
                    con.execute(
                        "UPDATE ejemplares SET estado='Disponible',id_sede_actual=id_sede WHERE id_ejemplar=?",
                        (id_ejemplar,))
                else:
                    con.execute(
                        "UPDATE ejemplares SET estado='Prestado',id_sede_actual=? WHERE id_ejemplar=?",
                        (destino,id_ejemplar))
        con.close()
        return ruta
    except Exception:
        # Limpiar solo el archivo nuevo; jamás la base habitual.
        if ruta.exists():
            ruta.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida",type=Path,default=Path("biblioteca_reportes_demo.db"))
    a = parser.parse_args()
    archivo = preparar(a.salida)
    print(f"Base de demostración creada: {archivo}")
    print("Incluye 18 préstamos, solicitudes, traslados y devoluciones ficticios.")
    print("biblioteca.db NO fue modificada.")


if __name__ == "__main__":
    main()
