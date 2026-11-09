"""Los selectores de registros deben permitir escribir, sin recorrer listas largas."""
import unittest
from contextlib import ExitStack
from unittest.mock import patch

import flet as ft

from interfaces.ui_moderno import selector_con_busqueda


class PaginaFalsa:
    def update(self):
        pass

    def show_dialog(self, dialogo):
        pass

    def pop_dialog(self):
        pass


class PruebasSelectoresBuscables(unittest.TestCase):
    def test_se_puede_buscar_por_dni_y_conservar_el_id(self):
        opciones = [
            ft.DropdownOption(key="41", text="Torres, Lucía - DNI 99001234"),
            ft.DropdownOption(key="59", text="Pérez, Ana - DNI 31000000"),
        ]
        selector = selector_con_busqueda(
            label="Socio (nombre, apellido o DNI)",
            options=opciones,
            width=410,
        )

        self.assertIsInstance(selector, ft.Dropdown)
        self.assertTrue(selector.editable)
        self.assertTrue(selector.enable_filter)
        self.assertTrue(selector.enable_search)
        self.assertEqual(selector.width, 410)
        self.assertIn("99001234", selector.options[0].text)
        self.assertIn("Torres", selector.options[0].text)
        selector.value = "41"
        self.assertEqual(selector.value, "41")

    def test_todos_los_selectores_de_registros_son_buscables(self):
        from interfaces.ventana_catalogo import VentanaCatalogo
        from interfaces.ventana_solicitudes import VentanaSolicitudes
        from interfaces.ventana_remitos import VentanaRemitos
        from interfaces.ventana_prestamos import VentanaPrestamos
        from interfaces.ventana_devoluciones import VentanaDevoluciones
        from interfaces.ventana_reservas import VentanaReservas
        from interfaces.ventana_consultas import VentanaConsultas

        rutas = (
            "interfaces.ventana_catalogo.CatalogoServicio",
            "interfaces.ventana_solicitudes.PrestamosServicio",
            "interfaces.ventana_remitos.RemitosServicio",
            "interfaces.ventana_prestamos.PrestamosEfectivosServicio",
            "interfaces.ventana_devoluciones.DevolucionesServicio",
            "interfaces.ventana_reservas.ReservasServicio",
            "interfaces.ventana_consultas.ConsultasBiblioredServicio",
        )
        pagina = PaginaFalsa()

        def buscar(control, nombre):
            campo = getattr(control, nombre)
            self.assertIsInstance(campo, ft.Dropdown)
            self.assertTrue(campo.editable, nombre)
            self.assertTrue(campo.enable_filter, nombre)
            self.assertTrue(campo.enable_search, nombre)

        with ExitStack() as context:
            for ruta in rutas:
                servicio = context.enter_context(patch(ruta)).return_value
                for metodo in (
                    "listar_libros", "listar_sedes_activas",
                    "listar_ejemplares", "listar_ejemplares_disponibles",
                    "listar_socios_habilitados", "listar_solicitudes",
                    "listar_pendientes", "listar_remitos",
                    "listar_solicitudes_listas", "listar_prestamos",
                    "listar_prestamos_activos", "listar_devoluciones",
                    "listar_pendientes_retorno", "listar_remitos_retorno",
                    "listar_disponibilidad", "listar_reservas", "inventario",
                ):
                    getattr(servicio, metodo).return_value = []
            context.enter_context(patch(
                "interfaces.ventana_consultas.consultar_socios",
                return_value=[]
            ))
            context.enter_context(patch(
                "interfaces.ventana_consultas.consultar_sedes",
                return_value=[]
            ))

            catalogo = VentanaCatalogo(pagina)
            catalogo.crear_contenido()
            catalogo._cambiar_seccion("ejemplares")
            for nombre in ("_libro", "_sede"):
                buscar(catalogo, nombre)

            solicitudes = VentanaSolicitudes(pagina, lambda: None)
            solicitudes.crear_contenido()
            for nombre in ("_socio", "_ejemplar", "_destino"):
                buscar(solicitudes, nombre)

            remitos = VentanaRemitos(pagina, lambda: None)
            remitos.crear_contenido()
            buscar(remitos, "_solicitud")

            prestamos = VentanaPrestamos(pagina, lambda: None)
            prestamos.crear_contenido()
            buscar(prestamos, "_solicitud")
            self.assertFalse(prestamos._plazo.editable)

            devoluciones = VentanaDevoluciones(pagina)
            devoluciones.crear_contenido()
            buscar(devoluciones, "_prestamo")
            self.assertFalse(devoluciones._estado_fisico.editable)
            devoluciones._cambiar("retornos")
            buscar(devoluciones, "_devolucion")

            reservas = VentanaReservas(pagina)
            reservas.crear_contenido()
            buscar(reservas, "_filtro_sede")
            reservas._cambiar("reservas")
            for nombre in ("_socio", "_libro", "_sede"):
                buscar(reservas, nombre)

            consultas = VentanaConsultas(pagina)
            consultas.crear_inventario()
            buscar(consultas, "_sede")
            consultas.crear_historial()
            buscar(consultas, "_socio")


if __name__ == "__main__":
    unittest.main()
