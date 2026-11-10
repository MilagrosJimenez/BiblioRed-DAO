"""Pruebas de integridad de reservas, solicitudes y disponibilidad.

Ejecutar desde la carpeta raíz:
    py -m unittest discover -s tests -v
No utiliza biblioteca.db: crea una base temporal aislada.
"""

import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from unittest.mock import patch

from clases.reserva import Reserva
from clases.solicitud_prestamo import SolicitudPrestamo
from datos import base_datos, catalogo_datos, prestamos_datos, remitos_datos, reservas_datos
from servicios.prestamos_servicio import PrestamosServicio


class PruebasReservasDisponibilidad(unittest.TestCase):

    def setUp(self):
        archivo = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        archivo.close()
        self.ruta = archivo.name
        self.parches = [
            patch.object(modulo, "RUTA_BASE_DATOS", self.ruta)
            for modulo in (
                base_datos, catalogo_datos, prestamos_datos,
                remitos_datos, reservas_datos
            )
        ]
        for parche in self.parches:
            parche.start()

        base_datos.crear_tabla_sedes()
        base_datos.crear_tabla_socios()
        catalogo_datos.crear_tablas_catalogo()
        prestamos_datos.crear_tabla_solicitudes()
        remitos_datos.crear_tablas_remitos()
        reservas_datos.crear_tabla_reservas()

        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            conexion.execute("""
                INSERT INTO sedes
                    (id_sede, nombre, direccion, telefono, horarios, activa)
                VALUES (1, 'Centro', 'Calle A', '123', '8-18', 1),
                       (2, 'Norte', 'Calle B', '456', '8-18', 1)
            """)
            conexion.execute("""
                INSERT INTO socios
                    (documento, nombre, apellido, telefono, correo, habilitado)
                VALUES ('TEST1', 'Ana', 'Ejemplo', '123', '', 1),
                       ('TEST2', 'Luis', 'Prueba', '123', '', 1)
            """)
            conexion.execute("""
                INSERT INTO libros (isbn, titulo, autor, editorial)
                VALUES ('TEST-ISBN', 'Libro de prueba', 'Autor', 'Editorial')
            """)
            conexion.execute("""
                INSERT INTO ejemplares
                    (codigo, id_libro, id_sede, id_sede_actual, estado)
                VALUES ('EJ-TEST', 1, 1, 1, 'Disponible')
            """)

    def tearDown(self):
        for parche in reversed(self.parches):
            parche.stop()
        os.unlink(self.ruta)

    def estado_ejemplar(self):
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            return conexion.execute(
                "SELECT estado FROM ejemplares WHERE id_ejemplar = 1"
            ).fetchone()[0]

    def disponibilidad(self, sede=1):
        for registro in reservas_datos.consultar_disponibilidad():
            if registro[0] == 1 and registro[3] == sede:
                return registro
        self.fail("No se encontró disponibilidad")

    def test_solicitud_directa_sin_reservas(self):
        self.assertEqual(self.disponibilidad()[6], 1)
        self.assertEqual(len(PrestamosServicio().listar_ejemplares_disponibles()), 1)
        solicitud = SolicitudPrestamo(2, 1, 1, 2)
        prestamos_datos.guardar_solicitud(solicitud)
        self.assertEqual(self.estado_ejemplar(), "Solicitado")

    def test_reserva_pendiente_tiene_prioridad_sobre_solicitud_directa(self):
        reservas_datos.guardar_reserva(Reserva(1, 1, 1))
        self.assertEqual(self.disponibilidad()[6], 0)
        self.assertEqual(self.disponibilidad()[7], 1)
        self.assertEqual(PrestamosServicio().listar_ejemplares_disponibles(), [])

        with self.assertRaises(ValueError):
            prestamos_datos.guardar_solicitud(
                SolicitudPrestamo(2, 1, 1, 1)
            )
        self.assertEqual(self.estado_ejemplar(), "Disponible")

    def test_atencion_y_cancelacion_restauran_cola(self):
        numero = reservas_datos.guardar_reserva(Reserva(1, 1, 1))
        solicitud_id = reservas_datos.atender_reserva(numero)
        self.assertEqual(self.estado_ejemplar(), "Solicitado")
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            estado = conexion.execute(
                "SELECT estado FROM reservas WHERE id_reserva = ?", (numero,)
            ).fetchone()[0]
        self.assertEqual(estado, "Atendida")

        # No se crea una segunda reserva para el mismo título mientras
        # sigue activa la solicitud originada por la reserva atendida.
        with self.assertRaises(ValueError):
            reservas_datos.guardar_reserva(Reserva(1, 1, 1))

        prestamos_datos.cancelar_solicitud(solicitud_id)
        self.assertEqual(self.estado_ejemplar(), "Disponible")
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            estado, solicitud_vinculada = conexion.execute(
                "SELECT estado, id_solicitud FROM reservas WHERE id_reserva = ?",
                (numero,)
            ).fetchone()
        self.assertEqual(estado, "Pendiente")
        self.assertIsNone(solicitud_vinculada)
        self.assertEqual(self.disponibilidad()[6], 0)
        self.assertGreater(reservas_datos.atender_reserva(numero), solicitud_id)

    def test_respetar_orden_de_reservas(self):
        primera = reservas_datos.guardar_reserva(Reserva(1, 1, 1))
        segunda = reservas_datos.guardar_reserva(Reserva(2, 1, 1))
        with self.assertRaises(ValueError):
            reservas_datos.atender_reserva(segunda)
        self.assertEqual(self.estado_ejemplar(), "Disponible")
        reservas_datos.cancelar_reserva(primera)
        reservas_datos.atender_reserva(segunda)
        self.assertEqual(self.estado_ejemplar(), "Solicitado")

    def test_transito_no_se_cuenta_como_presencia_fisica(self):
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            conexion.execute("""
                UPDATE ejemplares
                SET estado = 'En tránsito', id_sede_actual = 1
                WHERE id_ejemplar = 1
            """)
        self.assertEqual(self.disponibilidad(1)[5], 0)
        self.assertEqual(self.disponibilidad(1)[6], 0)

        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            conexion.execute("""
                UPDATE ejemplares
                SET estado = 'Recibido', id_sede_actual = 2
                WHERE id_ejemplar = 1
            """)
        self.assertEqual(self.disponibilidad(1)[5], 0)
        self.assertEqual(self.disponibilidad(2)[5], 1)
        self.assertEqual(self.disponibilidad(2)[6], 0)

    def test_reserva_en_sede_sin_copia_genera_pedido_interbibliotecario(self):
        # El ejemplar pertenece a Centro (1) y se retira en Norte (2).
        numero = reservas_datos.guardar_reserva(Reserva(1, 1, 2))
        solicitud_id = reservas_datos.atender_reserva(numero)
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            registro = conexion.execute("""
                SELECT id_sede_origen, id_sede_destino, tipo, estado
                FROM solicitudes_prestamo
                WHERE id_solicitud = ?
            """, (solicitud_id,)).fetchone()
        self.assertEqual(
            registro, (1, 2, "Interbibliotecario", "Pendiente de traslado")
        )
        self.assertEqual(self.estado_ejemplar(), "Solicitado")

    def test_cancelar_reserva_habilita_solicitud_directa(self):
        numero = reservas_datos.guardar_reserva(Reserva(1, 1, 1))
        reservas_datos.cancelar_reserva(numero)
        self.assertEqual(self.disponibilidad()[6], 1)
        prestamos_datos.guardar_solicitud(
            SolicitudPrestamo(2, 1, 1, 1)
        )
        self.assertEqual(self.estado_ejemplar(), "Solicitado")


if __name__ == "__main__":
    unittest.main()
