"""Pruebas de filtros y controles de diseño; no abren ventanas ni usan DB."""
import unittest
import flet as ft

from interfaces.ui_moderno import (
    normalizar, modernizar, texto_visible, buscador_de_tabla,
    buscador_de_tarjetas
)


class PaginaFalsa:
    def __init__(self):
        self.actualizaciones = 0

    def update(self):
        self.actualizaciones += 1


class PruebasBuscadores(unittest.TestCase):
    def test_normalizacion(self):
        self.assertEqual(normalizar("JIMÉNEZ"), "jimenez")
        self.assertEqual(normalizar("  María  "), "maria")

    def test_filtra_tabla_por_una_letra_y_numero(self):
        pagina = PaginaFalsa()
        tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Socio")),
                     ft.DataColumn(ft.Text("DNI"))],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Jiménez")), ft.DataCell(ft.Text("1001"))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Ana")), ft.DataCell(ft.Text("2450"))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Jorge")), ft.DataCell(ft.Text("765"))
                ])
            ]
        )
        panel = ft.Column([
            ft.Text("Socios registrados"),
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
        ])
        modernizar(panel, pagina)
        campos = [
            c for x in panel.controls if isinstance(x, ft.Row)
            for c in x.controls if isinstance(c, ft.TextField)
        ]
        self.assertEqual(len(campos), 1)
        campo = campos[0]
        campo.value = "j"
        campo.on_change(None)
        self.assertEqual(len(tabla.rows), 2)
        campo.value = "1"
        campo.on_submit(None)
        self.assertEqual(len(tabla.rows), 1)
        campo.value = "MARÍA"
        campo.on_change(None)
        self.assertEqual(len(tabla.rows), 0)
        campo.value = ""
        campo.on_change(None)
        self.assertEqual(len(tabla.rows), 3)

    def test_filtra_tarjetas_de_remitos(self):
        pagina = PaginaFalsa()
        tarjetas = ft.Column([
            ft.Container(content=ft.Text("Remito 1 - Libro A")),
            ft.Container(content=ft.Text("Remito 20 - Libro B"))
        ])
        panel = ft.Column([ft.Text("Remitos registrados"), tarjetas])
        modernizar(panel, pagina)
        campo = next(
            c for x in panel.controls if isinstance(x, ft.Row)
            for c in x.controls if isinstance(c, ft.TextField)
        )
        campo.value = "20"
        campo.on_change(None)
        self.assertEqual(len(tarjetas.controls), 1)
        self.assertIn("20", texto_visible(tarjetas.controls[0]))
        campo.value = ""
        campo.on_submit(None)
        self.assertEqual(len(tarjetas.controls), 2)

    def test_estructura_navegacion_moderna(self):
        from types import SimpleNamespace
        from interfaces.ventana_completa import VentanaCompleta

        class Pagina:
            def __init__(self):
                self.window = SimpleNamespace(width=0, height=0)
                self.controls = []

            def add(self, control):
                self.controls.append(control)

            def update(self):
                pass

        ventana = VentanaCompleta.__new__(VentanaCompleta)
        ventana._page = Pagina()
        ventana._contenido = ft.Column([])
        ventana._crear_estructura()
        self.assertEqual(len(ventana._nav_items), 12)
        self.assertEqual(ventana._pagina_activa, "Inicio")
        self.assertEqual(len(ventana._page.controls), 1)

    def test_button_y_controles_modernos(self):
        panel = ft.Column([
            ft.Container(
                bgcolor="white",
                content=ft.Column([
                    ft.TextField(label="Nombre"),
                    ft.Button("Guardar", bgcolor="#63BDEB")
                ])
            )
        ])
        modernizar(panel, PaginaFalsa())
        self.assertEqual(panel.controls[0].border_radius, 15)


class PruebaNavegacionCompleta(unittest.TestCase):
    def test_todas_las_pantallas_abren_con_base_temporal(self):
        import os
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import patch
        from datos import (
            base_datos, catalogo_datos, prestamos_datos, remitos_datos,
            prestamos_efectivos_datos, devoluciones_datos, reservas_datos,
            consultas_bibliored_datos
        )
        from interfaces.ventana_completa import VentanaCompleta

        class PaginaFalsa:
            def __init__(self):
                self.window = SimpleNamespace(width=0, height=0)
                self.controls = []

            def add(self, control):
                self.controls.append(control)

            def update(self):
                pass

            def show_dialog(self, dialogo):
                pass

            def pop_dialog(self):
                pass

        archivo = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        archivo.close()
        ruta = archivo.name
        parches = [
            patch.object(mod, "RUTA_BASE_DATOS", ruta)
            for mod in (
                base_datos, catalogo_datos, prestamos_datos, remitos_datos,
                prestamos_efectivos_datos, devoluciones_datos,
                reservas_datos, consultas_bibliored_datos,
            )
        ]
        try:
            for p in parches:
                p.start()
            base_datos.crear_tabla_sedes()
            base_datos.crear_tabla_socios()
            catalogo_datos.crear_tablas_catalogo()
            prestamos_datos.crear_tabla_solicitudes()
            remitos_datos.crear_tablas_remitos()
            prestamos_efectivos_datos.crear_tabla_prestamos()
            devoluciones_datos.crear_tablas_devoluciones()
            reservas_datos.crear_tabla_reservas()

            app = VentanaCompleta(PaginaFalsa())
            for nombre in (
                "_mostrar_sedes", "_mostrar_socios", "_mostrar_catalogo",
                "_mostrar_solicitudes", "_mostrar_remitos",
                "_mostrar_prestamos", "_mostrar_devoluciones",
                "_mostrar_reservas", "_mostrar_inventario",
                "_mostrar_historial_lecturas", "_mostrar_reportes",
                "_mostrar_inicio"
            ):
                with self.subTest(pantalla=nombre):
                    getattr(app, nombre)()

            # También se prueban las pantallas secundarias que se reconstruyen.
            from interfaces.ventana_catalogo import VentanaCatalogo
            from interfaces.ventana_devoluciones import VentanaDevoluciones
            from interfaces.ventana_reservas import VentanaReservas
            catalogo = VentanaCatalogo(app._page)
            catalogo.crear_contenido()
            catalogo._cambiar_seccion("ejemplares")
            devoluciones = VentanaDevoluciones(app._page)
            devoluciones.crear_contenido()
            devoluciones._cambiar("retornos")
            reservas = VentanaReservas(app._page)
            reservas.crear_contenido()
            reservas._cambiar("reservas")
        finally:
            for p in reversed(parches):
                p.stop()
            os.unlink(ruta)


if __name__ == "__main__":
    unittest.main()
