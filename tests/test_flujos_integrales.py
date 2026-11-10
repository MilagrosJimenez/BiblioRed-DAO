"""Pruebas de recorrido completo con SQLite temporal.

No utiliza la base de datos local de los usuarios.
"""
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from unittest.mock import patch

from clases.solicitud_prestamo import SolicitudPrestamo
from clases.prestamo import Prestamo
from clases.devolucion import Devolucion

from datos import (
    base_datos, catalogo_datos, prestamos_datos, remitos_datos,
    prestamos_efectivos_datos, devoluciones_datos,
    reservas_datos, consultas_bibliored_datos
)


class PruebasFlujosIntegrales(unittest.TestCase):
    def setUp(self):
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp.close()
        self.ruta = temp.name
        self.parches = [
            patch.object(mod, "RUTA_BASE_DATOS", self.ruta)
            for mod in (
                base_datos, catalogo_datos, prestamos_datos, remitos_datos,
                prestamos_efectivos_datos, devoluciones_datos,
                reservas_datos, consultas_bibliored_datos
            )
        ]
        for p in self.parches:
            p.start()
        base_datos.crear_tabla_sedes()
        base_datos.crear_tabla_socios()
        catalogo_datos.crear_tablas_catalogo()
        prestamos_datos.crear_tabla_solicitudes()
        remitos_datos.crear_tablas_remitos()
        prestamos_efectivos_datos.crear_tabla_prestamos()
        devoluciones_datos.crear_tablas_devoluciones()
        reservas_datos.crear_tabla_reservas()
        with closing(sqlite3.connect(self.ruta)) as db, db:
            db.executescript("""
                INSERT INTO sedes(id_sede,nombre,direccion,telefono,horarios,activa)
                  VALUES (1,'Centro','A','11','8-18',1),
                         (2,'Norte','B','22','8-18',1);
                INSERT INTO socios(documento,nombre,apellido,telefono,correo,habilitado)
                  VALUES('P1','Ana','Prueba','1','test@example.invalid',1);
                INSERT INTO libros(isbn,titulo,autor,editorial)
                  VALUES('ISBN-1','Libro probado','Autor','Editorial');
                INSERT INTO ejemplares(codigo,id_libro,id_sede,id_sede_actual,estado)
                  VALUES('EJ-1',1,1,1,'Disponible');
            """)

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()
        os.unlink(self.ruta)

    def estado_ejemplar(self):
        with closing(sqlite3.connect(self.ruta)) as db, db:
            return db.execute("""
                SELECT estado, id_sede_actual FROM ejemplares WHERE id_ejemplar = 1
            """).fetchone()

    def test_local_solicitud_prestamo_devolucion(self):
        prestamos_datos.guardar_solicitud(SolicitudPrestamo(1, 1, 1, 1))
        self.assertEqual(self.estado_ejemplar(), ("Solicitado", 1))
        id_prestamo = prestamos_efectivos_datos.registrar_prestamo(Prestamo(1, 7))
        self.assertEqual(self.estado_ejemplar(), ("Prestado", 1))
        devoluciones_datos.registrar_devolucion(Devolucion(id_prestamo, "Bueno"))
        self.assertEqual(self.estado_ejemplar(), ("Disponible", 1))
        self.assertEqual(
            consultas_bibliored_datos.consultar_historial_lecturas(1)[0][5],
            "Devuelto"
        )

    def test_interbibliotecario_ida_prestamo_regreso(self):
        prestamos_datos.guardar_solicitud(SolicitudPrestamo(1, 1, 1, 2))
        id_remito = remitos_datos.empaquetar_solicitud(1)
        self.assertEqual(self.estado_ejemplar(), ("Empaquetado", 1))
        remitos_datos.avanzar_remito(id_remito, "En tránsito")
        self.assertEqual(self.estado_ejemplar(), ("En tránsito", 1))
        remitos_datos.avanzar_remito(id_remito, "Recibido")
        self.assertEqual(self.estado_ejemplar(), ("Recibido", 2))
        id_prestamo = prestamos_efectivos_datos.registrar_prestamo(Prestamo(1, 14))
        self.assertEqual(self.estado_ejemplar(), ("Prestado", 2))
        id_devolucion = devoluciones_datos.registrar_devolucion(
            Devolucion(id_prestamo, "Bueno", "Sin daños")
        )
        self.assertEqual(self.estado_ejemplar(), ("Pendiente de retorno", 2))
        id_retorno = devoluciones_datos.preparar_retorno(id_devolucion)
        self.assertEqual(self.estado_ejemplar(), ("Retorno empaquetado", 2))
        devoluciones_datos.avanzar_retorno(id_retorno, "En tránsito")
        self.assertEqual(self.estado_ejemplar(), ("Retorno en tránsito", 2))
        devoluciones_datos.avanzar_retorno(id_retorno, "Recibido")
        self.assertEqual(self.estado_ejemplar(), ("Disponible", 1))

        ida = remitos_datos.consultar_historial_remito(id_remito)
        regreso = devoluciones_datos.consultar_historial_retorno(id_retorno)
        self.assertEqual([x[0] for x in ida],
                         ["Empaquetado", "En tránsito", "Recibido"])
        self.assertEqual([x[0] for x in regreso],
                         ["Empaquetado", "En tránsito", "Recibido"])
        self.assertTrue(all(x[2] for x in ida))
        self.assertTrue(all(x[2] for x in regreso))
        movimientos = consultas_bibliored_datos.reporte_movimientos()
        self.assertEqual(sum(fila[2] for fila in movimientos), 2)


if __name__ == "__main__":
    unittest.main()
