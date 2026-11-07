
import flet as ft

from interfaces.ventana_flet import VentanaFlet
from interfaces.ventana_socios import VentanaSocios
from interfaces.ventana_catalogo import VentanaCatalogo
from interfaces.ventana_solicitudes import VentanaSolicitudes
from interfaces.ventana_remitos import VentanaRemitos
from interfaces.ventana_prestamos import VentanaPrestamos
from interfaces.ventana_devoluciones import VentanaDevoluciones
from interfaces.ventana_reservas import VentanaReservas
from interfaces.ventana_consultas import VentanaConsultas


class VentanaCompleta(VentanaFlet):

    def _crear_estructura(self):
        encabezado = ft.Container(
            bgcolor="#FFFFFF",
            padding=24,
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "BiblioRed",
                                size=29,
                                weight=ft.FontWeight.BOLD,
                                color=self._azul
                            ),
                            ft.Text(
                                "Sistema de préstamos interbibliotecarios",
                                size=13,
                                color="#63839A"
                            )
                        ],
                        spacing=2
                    ),
                    self._crear_logo()
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        opciones_menu = [
            ("Inicio", self._mostrar_inicio),
            ("Administrar sedes", self._mostrar_sedes),
            ("Administrar socios", self._mostrar_socios),
            ("Catálogo y ejemplares", self._mostrar_catalogo),
            ("Solicitudes de préstamo", self._mostrar_solicitudes),
            ("Remitos y traslados", self._mostrar_remitos),
            ("Préstamos efectivos", self._mostrar_prestamos),
            ("Devoluciones", self._mostrar_devoluciones),
            ("Reservas y disponibilidad", self._mostrar_reservas),
            ("Inventario por códigos", self._mostrar_inventario),
            ("Historial de lecturas", self._mostrar_historial_lecturas),
            ("Reportes", self._mostrar_reportes)
        ]

        controles_menu = [
            ft.Text(
                "NAVEGACIÓN",
                size=12,
                weight=ft.FontWeight.BOLD,
                color="#B6D8EE"
            )
        ]

        for texto, accion in opciones_menu:
            controles_menu.append(
                ft.Button(
                    texto,
                    on_click=accion,
                    bgcolor="#BCE7FF",
                    color=self._azul,
                    width=195
                )
            )

        controles_menu.extend([
            ft.Container(height=12),
            ft.Text("DAO 2026 - UTN FRC", size=11, color="#A9C6DA")
        ])

        menu = ft.Container(
            bgcolor=self._azul,
            width=240,
            padding=20,
            content=ft.Column(
                controls=controles_menu,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        )

        cuerpo = ft.Row(
            controls=[
                menu,
                ft.Container(
                    content=self._contenido,
                    padding=28,
                    expand=True
                )
            ],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )

        self._page.add(
            ft.Column(
                controls=[
                    encabezado,
                    cuerpo
                ],
                spacing=0,
                expand=True
            )
        )

    def _mostrar_socios(self, e=None):
        pantalla = VentanaSocios(
            self._page,
            self._mostrar_socios
        )

        self._contenido.controls = [
            self._crear_titulo(
                "Administrar socios",
                "Registrá, consultá y modificá los socios de la red"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_catalogo(self, e=None):
        pantalla = VentanaCatalogo(self._page)

        self._contenido.controls = [
            self._crear_titulo(
                "Catálogo y ejemplares",
                "Administrá los libros y sus copias físicas por sede"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_solicitudes(self, e=None):
        pantalla = VentanaSolicitudes(
            self._page,
            self._mostrar_solicitudes
        )

        self._contenido.controls = [
            self._crear_titulo(
                "Solicitudes de préstamo",
                "Solicitudes locales e interbibliotecarias"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_remitos(self, e=None):
        pantalla = VentanaRemitos(
            self._page,
            self._mostrar_remitos
        )

        self._contenido.controls = [
            self._crear_titulo(
                "Remitos y traslados",
                "Preparación, despacho, recepción y trazabilidad"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_prestamos(self, e=None):
        pantalla = VentanaPrestamos(
            self._page,
            self._mostrar_prestamos
        )

        self._contenido.controls = [
            self._crear_titulo(
                "Préstamos efectivos",
                "Registrá la entrega y el vencimiento de ejemplares"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_devoluciones(self, e=None):
        pantalla = VentanaDevoluciones(self._page)

        self._contenido.controls = [
            self._crear_titulo(
                "Devoluciones",
                "Estado físico, cierre de préstamos y retorno de ejemplares"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_reservas(self, e=None):
        pantalla = VentanaReservas(self._page)

        self._contenido.controls = [
            self._crear_titulo(
                "Reservas y disponibilidad",
                "Consulta de ejemplares y gestión de reservas por sede"
            ),
            pantalla.crear_contenido()
        ]

        self._page.update()

    def _mostrar_inventario(self, e=None):
        pantalla = VentanaConsultas(self._page)
        self._contenido.controls = [
            self._crear_titulo("Inventario por códigos",
                              "Consulta de ejemplares, sede propietaria y ubicación"),
            pantalla.crear_inventario()
        ]
        self._page.update()

    def _mostrar_historial_lecturas(self, e=None):
        pantalla = VentanaConsultas(self._page)
        self._contenido.controls = [
            self._crear_titulo("Historial de lecturas",
                              "Préstamos y devoluciones por socio"),
            pantalla.crear_historial()
        ]
        self._page.update()

    def _mostrar_reportes(self, e=None):
        pantalla = VentanaConsultas(self._page)
        self._contenido.controls = [
            self._crear_titulo("Reportes de BiblioRed",
                              "Cuatro informes definidos en el PDF entregado"),
            pantalla.crear_reportes()
        ]
        self._page.update()
