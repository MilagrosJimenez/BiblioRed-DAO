"""Pantallas complementarias: inventario, historial y reportes del alcance."""
import flet as ft
from datos.base_datos import consultar_sedes, consultar_socios
from servicios.consultas_bibliored_servicio import ConsultasBiblioredServicio
from interfaces.ui_moderno import normalizar, personalizar_controles


class VentanaConsultas:
    def __init__(self, page):
        self._page = page
        self._servicio = ConsultasBiblioredServicio()
        self._azul = "#153D63"

    def _dialogo(self, titulo, mensaje):
        self._page.show_dialog(ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(str(mensaje)),
            actions=[ft.TextButton(
                "Aceptar", on_click=lambda e: self._page.pop_dialog()
            )]
        ))

    def _tarjeta(self, titulo, lineas):
        return ft.Container(
            bgcolor="#F1F7FC",
            border_radius=10,
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Text(titulo, weight=ft.FontWeight.BOLD, color=self._azul),
                    *[ft.Text(str(linea), size=12) for linea in lineas]
                ],
                spacing=4
            )
        )

    def _panel(self, titulo, controles):
        return ft.Container(
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=12,
            content=ft.Column(
                controls=[ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD,
                                  color=self._azul), *controles],
                spacing=14
            )
        )

    def crear_inventario(self):
        self._codigo = ft.TextField(
            label="Código del ejemplar",
            hint_text="Buscá por código, título, estado o sede...",
            width=290,
            on_change=self._buscar_inventario,
            on_submit=self._buscar_inventario,
        )
        self._sede = ft.Dropdown(
            label="Filtrar por sede propietaria o ubicación", width=290,
            value="todas",
            on_select=self._buscar_inventario,
            options=[ft.DropdownOption(key="todas", text="Todas las sedes")] + [
                ft.DropdownOption(key=str(s[0]), text=s[1])
                for s in consultar_sedes()
            ]
        )
        self._resultados = ft.Column(spacing=8)
        self._buscar_inventario()
        return self._panel("Inventario por código y sede", [
            ft.Row([
                self._codigo, self._sede,
                ft.Button("Buscar", on_click=self._buscar_inventario)
            ], wrap=True, spacing=10),
            self._resultados
        ])

    def _buscar_inventario(self, e=None):
        sede = self._sede.value
        filas = self._servicio.inventario(
            "",
            None if sede in (None, "todas") else int(sede)
        )
        termino = normalizar(self._codigo.value)
        filas = [
            fila for fila in filas
            if not termino or termino in normalizar(" ".join(
                str(valor) for valor in fila
            ))
        ]
        self._resultados.controls = [
            self._tarjeta(f"{f[0]} | {f[1]}", [
                f"Estado: {f[2]}",
                f"Sede propietaria: {f[3]}",
                f"Ubicación registrada: {f[4]}"
            ]) for f in filas
        ] or [ft.Text("No se encontraron ejemplares.")]
        personalizar_controles(self._resultados)
        if e is not None:
            self._page.update()

    def crear_historial(self):
        self._socio = ft.Dropdown(
            label="Socio", width=360,
            options=[
                ft.DropdownOption(
                    key=str(s[0]), text=f"{s[3]}, {s[2]} - DNI {s[1]}"
                ) for s in consultar_socios()
            ]
        )
        self._resultados = ft.Column(spacing=8)
        return self._panel("Historial de lecturas por socio", [
            ft.Row([
                self._socio,
                ft.Button("Consultar historial", on_click=self._buscar_historial)
            ], wrap=True),
            self._resultados
        ])

    def _buscar_historial(self, e):
        if not self._socio.value:
            self._dialogo("Falta seleccionar", "Elegí un socio.")
            return
        filas = self._servicio.historial(int(self._socio.value))
        self._resultados.controls = [
            self._tarjeta(f"{f[0]} | {f[1]}", [
                f"Entrega: {f[2]} | Vencimiento: {f[3]}",
                f"Devolución: {f[4] or 'Aún no devuelto'} | Estado: {f[5]}"
            ]) for f in filas
        ] or [ft.Text("Este socio todavía no tiene préstamos registrados.")]
        personalizar_controles(self._resultados)
        self._page.update()

    def crear_reportes(self):
        from datos.consultas_bibliored_datos import REPORTES

        def generar(e, clave):
            try:
                from servicios.reportes_pdf import generar_reporte
                archivo = generar_reporte(clave)
                self._dialogo(
                    "Reporte generado",
                    "PDF guardado en:\\n" + archivo +
                    "\\n\\nAbrilo desde el Explorador de archivos."
                )
            except ModuleNotFoundError as error:
                self._dialogo(
                    "Falta una biblioteca",
                    "Instalá ReportLab con: py -m pip install reportlab\\n" +
                    str(error)
                )
            except Exception as error:
                self._dialogo("Error al generar reporte", str(error))

        tarjetas = [
            ft.Container(
                bgcolor="#F1F7FC",
                border_radius=10,
                padding=14,
                content=ft.Row(
                    controls=[
                        ft.Text(datos[0], expand=True, color=self._azul),
                        ft.Button(
                            "Generar PDF",
                            on_click=lambda e, c=clave: generar(e, c)
                        )
                    ]
                )
            ) for clave, datos in REPORTES.items()
        ]
        return self._panel("Cuatro reportes obligatorios", [
            ft.Text(
                "Los archivos se guardan en reportes_generados dentro del proyecto.",
                size=12
            ),
            *tarjetas
        ])
