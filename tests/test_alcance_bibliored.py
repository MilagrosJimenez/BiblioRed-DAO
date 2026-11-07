"""Pruebas de contrato: patrones, informes, inventario e historial.

Usa una base SQLite temporal. No abre ni modifica biblioteca.db.
"""
import os
import sqlite3
import tempfile
import unittest
from datetime import date
from unittest.mock import patch

from clases.estado_remito import construir_estado
from clases.estrategia_plazo import (
    Plazo7Dias, Plazo14Dias, Plazo21Dias, seleccionar_estrategia
)
from clases.prestamo import Prestamo
from clases.remito import Remito
from clases.remito_retorno import RemitoRetorno
from datos import (
    base_datos, catalogo_datos, prestamos_datos, remitos_datos,
    prestamos_efectivos_datos, devoluciones_datos, reservas_datos,
    consultas_bibliored_datos,
)


class PruebaPatrones(unittest.TestCase):
    def test_strategy_7_14_21(self):
        fecha = date(2026, 11, 7)
        self.assertEqual(Plazo7Dias().calcular(fecha).isoformat(), "2026-11-14")
        self.assertEqual(Plazo14Dias().calcular(fecha).isoformat(), "2026-11-21")
        self.assertEqual(Plazo21Dias().calcular(fecha).isoformat(), "2026-11-28")
        with self.assertRaises(ValueError):
            seleccionar_estrategia(15)
        self.assertTrue(Prestamo(1, 7).fecha_vencimiento)

    def test_state_ida_y_retorno(self):
        ida = Remito(1, 1, 1, 2)
        retorno = RemitoRetorno(1)
        for remito in (ida, retorno):
            self.assertEqual(remito.estado, "Empaquetado")
            with self.assertRaises(ValueError):
                remito.recibir()
            remito.despachar()
            self.assertEqual(remito.estado, "En tránsito")
            with self.assertRaises(ValueError):
                remito.despachar()
            remito.recibir()
            self.assertEqual(remito.estado, "Recibido")
            with self.assertRaises(ValueError):
                remito.recibir()
        with self.assertRaises(ValueError):
            construir_estado("Pendiente")


class PruebaConsultas(unittest.TestCase):
    def setUp(self):
        temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp.close()
        self.ruta = temp.name
        self.parches = [
            patch.object(modulo, "RUTA_BASE_DATOS", self.ruta)
            for modulo in (
                base_datos, catalogo_datos, prestamos_datos, remitos_datos,
                prestamos_efectivos_datos, devoluciones_datos,
                reservas_datos, consultas_bibliored_datos,
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
        with sqlite3.connect(self.ruta) as conexion:
            conexion.execute("""
                INSERT INTO sedes(id_sede,nombre,direccion,telefono,horarios,activa)
                VALUES(1,'Centro','C','1','8-18',1),(2,'Norte','N','2','8-18',1)
            """)
            conexion.execute("""
                INSERT INTO socios(documento,nombre,apellido,telefono,correo,habilitado)
                VALUES('X1','Ana','Prueba','1','a@test.invalid',1)
            """)
            conexion.execute("""
                INSERT INTO libros(isbn,titulo,autor,editorial)
                VALUES('ISBN1','Un libro','Autor','Editorial')
            """)
            conexion.execute("""
                INSERT INTO ejemplares(codigo,id_libro,id_sede,id_sede_actual,estado)
                VALUES('E1',1,1,1,'Disponible')
            """)

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()
        os.unlink(self.ruta)

    def test_inventario_busca_codigo_y_ubicacion(self):
        filas = consultas_bibliored_datos.consultar_inventario("E1", 1)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][3], "Centro")
        self.assertEqual(filas[0][4], "Centro")
        self.assertEqual(consultas_bibliored_datos.consultar_inventario("OTRO"), [])

    def test_lecturas_desde_prestamos(self):
        with sqlite3.connect(self.ruta) as db:
            db.execute("""
                INSERT INTO solicitudes_prestamo(
                    id_socio,id_ejemplar,id_sede_origen,id_sede_destino,tipo,estado
                ) VALUES(1,1,1,1,'Local','Prestada')
            """)
            db.execute("""
                INSERT INTO prestamos(
                    id_solicitud,id_socio,id_ejemplar,
                    fecha_prestamo,fecha_vencimiento,fecha_devolucion,estado
                ) VALUES(1,1,1,'2026-10-01','2026-10-08','2026-10-07','Devuelto')
            """)
        filas = consultas_bibliored_datos.consultar_historial_lecturas(1)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][0], "Un libro")
        self.assertEqual(filas[0][4], "2026-10-07")

    def test_cuatro_reportes_ejecutan_y_muestran_datos(self):
        from datos.consultas_bibliored_datos import REPORTES
        self.assertEqual(len(REPORTES), 4)
        for clave, (titulo, columnas, consulta) in REPORTES.items():
            filas = consulta()
            self.assertIsInstance(filas, list, clave)
            self.assertTrue(titulo)
            self.assertTrue(columnas)
        self.assertEqual(consultas_bibliored_datos.reporte_disponibilidad()[0][2], 1)

    def test_generar_pdf_real_con_reportlab(self):
        from servicios.reportes_pdf import generar_reporte
        archivo = generar_reporte("disponibilidad")
        try:
            with open(archivo, "rb") as pdf:
                self.assertEqual(pdf.read(5), b"%PDF-")
            self.assertGreater(os.path.getsize(archivo), 1000)
        finally:
            os.unlink(archivo)

    def test_migracion_observaciones_no_pierde_historial(self):
        with sqlite3.connect(self.ruta) as db:
            for tabla in ("historial_remitos", "historial_retornos"):
                columnas = [
                    col[1] for col in db.execute("PRAGMA table_info(" + tabla + ")")
                ]
                self.assertIn("observacion", columnas)
        # Segunda inicialización idempotente
        remitos_datos.crear_tablas_remitos()
        devoluciones_datos.crear_tablas_devoluciones()


if __name__ == "__main__":
    unittest.main()
