"""Pruebas de aceptación de los seis primeros módulos de BiblioRed.

Se ejecutan sobre una base SQLite temporal. No acceden a biblioteca.db.
El recorrido funcional corresponde a los procesos 1-5 del PDF entregado,
más el panel de Inicio.
"""
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import patch

from clases.sede import Sede
from clases.socio import Socio
from datos import (
    base_datos, catalogo_datos, prestamos_datos, remitos_datos,
    reservas_datos,
)
from servicios.catalogo_servicio import CatalogoServicio
from servicios.prestamos_servicio import PrestamosServicio
from servicios.remitos_servicio import RemitosServicio
from interfaces.ventana_remitos import VentanaRemitos


class PruebasEtapaUno(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temporal.close()
        self.ruta = temporal.name
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

        self.centro = Sede(9001, "Biblioteca Prueba DAO",
                           "Calle 123", "351111", "Lunes a viernes de 09:00 a 18:00")
        self.norte = Sede(9002, "Biblioteca Norte",
                          "Calle 456", "351222", "Viernes a lunes: atención 24 horas")
        self.assertTrue(base_datos.guardar_sede(self.centro))
        self.assertTrue(base_datos.guardar_sede(self.norte))
        self.socia = Socio(None, "99001234", "Lucía", "Prueba", "351333", "")
        self.assertTrue(base_datos.guardar_socio(self.socia))
        self.servicio_catalogo = CatalogoServicio()
        self.servicio_prestamos = PrestamosServicio()
        self.servicio_remitos = RemitosServicio()
        self.servicio_catalogo.registrar_libro(
            "9780000000001", "Libro de prueba DAO",
            "Autora Prueba", "Editorial Prueba"
        )

    def tearDown(self):
        for parche in reversed(self.parches):
            parche.stop()
        os.unlink(self.ruta)

    def datos_socio(self):
        return base_datos.consultar_socios()[0]

    def datos_libro(self):
        return self.servicio_catalogo.listar_libros()[0]

    def crear_copia(self, codigo="DAO-EJ-01"):
        self.servicio_catalogo.registrar_ejemplar(codigo, 1, 9001)
        return self.servicio_catalogo.listar_ejemplares()[0]

    def test_inicio_refleja_datos_reales(self):
        # Inicio consume estas consultas para contar sedes, socios y sus estados.
        sedes = base_datos.consultar_sedes()
        socios = base_datos.consultar_socios()
        self.assertEqual(len(sedes), 2)
        self.assertEqual(sum(s[5] == 1 for s in sedes), 2)
        self.assertEqual(len(socios), 1)
        self.assertEqual(self.datos_libro()[5], 0)

    def test_sedes_registro_duplicado_edicion_baja_y_reactivacion(self):
        self.assertFalse(base_datos.guardar_sede(self.centro))
        self.centro.actualizar_datos(
            self.centro.nombre, "Calle 999", "351444",
            self.centro.horarios
        )
        base_datos.actualizar_datos_sede(self.centro)
        fila = next(s for s in base_datos.consultar_sedes() if s[0] == 9001)
        self.assertEqual(fila[2], "Calle 999")
        self.assertEqual(fila[4], "Lunes a viernes de 09:00 a 18:00")
        self.centro.dar_de_baja()
        base_datos.actualizar_estado_sede(self.centro)
        self.assertEqual(
            [s[0] for s in self.servicio_catalogo.listar_sedes_activas()], [9002]
        )
        with self.assertRaises(ValueError):
            self.servicio_catalogo.registrar_ejemplar("NO-VALIDO", 1, 9001)
        self.centro.reactivar()
        base_datos.actualizar_estado_sede(self.centro)
        self.assertIn(
            9001, [s[0] for s in self.servicio_catalogo.listar_sedes_activas()]
        )

    def test_socios_alta_duplicado_edicion_y_restriccion(self):
        self.assertFalse(base_datos.guardar_socio(self.socia))
        dato = self.datos_socio()
        nueva = Socio(dato[0], dato[1], "Lucía", "Torres",
                      "351555", "lucia@ejemplo.com")
        base_datos.actualizar_datos_socio(nueva)
        self.assertEqual(self.datos_socio()[3], "Torres")
        nueva.inhabilitar()
        base_datos.actualizar_estado_socio(nueva)
        self.assertEqual(self.servicio_prestamos.listar_socios_habilitados(), [])
        nueva.habilitar()
        base_datos.actualizar_estado_socio(nueva)
        self.assertEqual(len(self.servicio_prestamos.listar_socios_habilitados()), 1)

    def test_catalogo_isbn_y_codigo_unicos(self):
        with self.assertRaisesRegex(ValueError, "ISBN"):
            self.servicio_catalogo.registrar_libro(
                "9780000000001", "Duplicado", "Autora", "Editorial"
            )
        self.crear_copia()
        with self.assertRaisesRegex(ValueError, "código"):
            self.servicio_catalogo.registrar_ejemplar("DAO-EJ-01", 1, 9001)
        libro = self.datos_libro()
        self.assertEqual(libro[5], 1)
        self.assertEqual(libro[6], 1)
        self.assertEqual(self.servicio_catalogo.listar_ejemplares()[0][5],
                         "Disponible")
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            sede_actual = conexion.execute("""
                SELECT id_sede_actual FROM ejemplares WHERE codigo = 'DAO-EJ-01'
            """).fetchone()[0]
        self.assertEqual(sede_actual, 9001)
        ficha = self.servicio_catalogo.listar_ejemplares()[0]
        self.assertEqual(ficha[4], "Biblioteca Prueba DAO")
        self.assertEqual(ficha[8], "Biblioteca Prueba DAO")

    def test_solicitud_local_y_cancelacion(self):
        copia = self.crear_copia()
        tipo = self.servicio_prestamos.registrar(
            self.datos_socio()[0], copia[0], 9001
        )
        self.assertEqual(tipo, "Local")
        self.assertEqual(self.servicio_prestamos.listar_solicitudes()[0][8],
                         "Pendiente")
        self.assertEqual(self.servicio_prestamos.listar_ejemplares_disponibles(),
                         [])
        with self.assertRaises(ValueError):
            self.servicio_prestamos.registrar(
                self.datos_socio()[0], copia[0], 9001
            )
        self.servicio_prestamos.cancelar(1)
        self.assertEqual(
            self.servicio_prestamos.listar_solicitudes()[0][8], "Cancelada"
        )
        self.assertEqual(
            len(self.servicio_prestamos.listar_ejemplares_disponibles()), 1
        )

    def test_solicitud_bloqueada_si_sede_destino_inactiva(self):
        copia = self.crear_copia()
        self.norte.dar_de_baja()
        base_datos.actualizar_estado_sede(self.norte)
        with self.assertRaisesRegex(ValueError, "destino"):
            self.servicio_prestamos.registrar(
                self.datos_socio()[0], copia[0], 9002
            )
        self.assertEqual(self.servicio_prestamos.listar_solicitudes(), [])
        self.assertEqual(
            self.servicio_catalogo.listar_ejemplares()[0][5], "Disponible"
        )

    def test_remito_empaquetar_despachar_recibir_y_trazabilidad(self):
        copia = self.crear_copia()
        tipo = self.servicio_prestamos.registrar(
            self.datos_socio()[0], copia[0], 9002
        )
        self.assertEqual(tipo, "Interbibliotecario")
        self.assertEqual(len(self.servicio_remitos.listar_pendientes()), 1)
        numero = self.servicio_remitos.empaquetar(1)
        self.assertEqual(self.servicio_remitos.listar_remitos()[0][5],
                         "Empaquetado")
        with self.assertRaises(ValueError):
            self.servicio_remitos.empaquetar(1)
        self.assertEqual(self.servicio_remitos.cambiar_estado(numero),
                         "En tránsito")
        self.assertEqual(self.servicio_remitos.cambiar_estado(numero),
                         "Recibido")
        with self.assertRaises(ValueError):
            self.servicio_remitos.cambiar_estado(numero)
        historial = self.servicio_remitos.ver_historial(numero)
        self.assertEqual([f[0] for f in historial],
                         ["Empaquetado", "En tránsito", "Recibido"])
        self.assertTrue(all(len(f) == 3 and f[2] for f in historial))
        with closing(sqlite3.connect(self.ruta)) as conexion, conexion:
            fila = conexion.execute("""
                SELECT estado, id_sede_actual FROM ejemplares
                WHERE id_ejemplar = ?
            """, (copia[0],)).fetchone()
        self.assertEqual(fila, ("Recibido", 9002))
        ficha = self.servicio_catalogo.listar_ejemplares()[0]
        self.assertEqual(ficha[4], "Biblioteca Prueba DAO")
        self.assertEqual(ficha[8], "Biblioteca Norte")

    def test_ver_historial_en_pantalla_muestra_observacion(self):
        # Evita la regresión donde el diálogo intentaba desempaquetar
        # dos campos aunque la consulta devolvía tres.
        pantalla = VentanaRemitos.__new__(VentanaRemitos)
        pantalla._servicio = SimpleNamespace(
            ver_historial=lambda numero: [
                ("Empaquetado", "2026-11-07 10:00", "Ejemplar preparado"),
                ("En tránsito", "2026-11-07 11:00", "Despachado")
            ]
        )
        dialogos = []
        pantalla._mensaje = lambda titulo, texto: dialogos.append((titulo, texto))
        pantalla._mostrar_historial(21)
        self.assertEqual(len(dialogos), 1)
        self.assertIn("remito N.º 21", dialogos[0][0])
        self.assertIn("Ejemplar preparado", dialogos[0][1])
        self.assertIn("En tránsito", dialogos[0][1])


if __name__ == "__main__":
    unittest.main()
