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


if __name__ == "__main__":
    unittest.main()
