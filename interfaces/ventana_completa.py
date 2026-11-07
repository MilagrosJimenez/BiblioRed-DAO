"""Interfaz principal moderna de BiblioRed. No altera casos de uso ni SQLite."""
import flet as ft

from datos.base_datos import consultar_sedes, consultar_socios
from datos.reservas_datos import consultar_reservas
from datos.prestamos_efectivos_datos import consultar_prestamos

from interfaces.ventana_flet import VentanaFlet
from interfaces.ventana_socios import VentanaSocios
from interfaces.ventana_catalogo import VentanaCatalogo
from interfaces.ventana_solicitudes import VentanaSolicitudes
from interfaces.ventana_remitos import VentanaRemitos
from interfaces.ventana_prestamos import VentanaPrestamos
from interfaces.ventana_devoluciones import VentanaDevoluciones
from interfaces.ventana_reservas import VentanaReservas
from interfaces.ventana_consultas import VentanaConsultas
from interfaces.ui_moderno import (
    modernizar, AZUL, AZUL_OSCURO, TINTA, APAGADO, FONDO, BORDE
)


class VentanaCompleta(VentanaFlet):

    def _crear_estructura(self):
        self._page.window.width = 1280
        self._page.window.height = 740
        self._page.bgcolor = FONDO
        self._azul = TINTA
        self._celeste = AZUL
        self._nav_items = {}
        self._pagina_activa = "Inicio"

        marca = ft.Column(
            controls=[
                ft.Row([
                    ft.Container(
                        content=ft.Text("B", size=22, color="#FFFFFF",
                                        weight=ft.FontWeight.BOLD),
                        width=42, height=42, bgcolor=AZUL, border_radius=12,
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Column([
                        ft.Text("BiblioRed", size=24, weight=ft.FontWeight.BOLD,
                                color=TINTA),
                        ft.Text("GESTIÓN BIBLIOTECARIA", size=10, color=APAGADO,
                                weight=ft.FontWeight.BOLD)
                    ], spacing=0)
                ], spacing=12)
            ],
            spacing=0
        )
        encabezado = ft.Container(
            height=94,
            bgcolor="#FFFFFF",
            padding=ft.Padding.symmetric(horizontal=26, vertical=12),
            border=ft.Border.only(bottom=ft.BorderSide(1, BORDE)),
            content=ft.Row([
                marca,
                self._crear_logo()
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        grupos = [
            ("GENERAL", [
                ("Inicio", "HOME_ROUNDED", self._mostrar_inicio),
                ("Administrar sedes", "ACCOUNT_BALANCE_OUTLINED", self._mostrar_sedes),
                ("Administrar socios", "PEOPLE_OUTLINE_ROUNDED", self._mostrar_socios),
                ("Catálogo y ejemplares", "MENU_BOOK_OUTLINED", self._mostrar_catalogo),
            ]),
            ("CIRCULACIÓN", [
                ("Solicitudes de préstamo", "DESCRIPTION_OUTLINED", self._mostrar_solicitudes),
                ("Remitos y traslados", "LOCAL_SHIPPING_OUTLINED", self._mostrar_remitos),
                ("Préstamos efectivos", "AUTO_STORIES_OUTLINED", self._mostrar_prestamos),
                ("Devoluciones", "KEYBOARD_RETURN_OUTLINED", self._mostrar_devoluciones),
                ("Reservas y disponibilidad", "EVENT_AVAILABLE_OUTLINED", self._mostrar_reservas),
            ]),
            ("CONSULTAS Y ANÁLISIS", [
                ("Inventario por códigos", "INVENTORY_2_OUTLINED", self._mostrar_inventario),
                ("Historial de lecturas", "HISTORY_OUTLINED", self._mostrar_historial_lecturas),
                ("Reportes", "BAR_CHART_OUTLINED", self._mostrar_reportes),
            ])
        ]
        controles = [
            ft.Container(
                content=ft.Text("ESPACIO DE TRABAJO", size=11,
                                weight=ft.FontWeight.BOLD, color="#B3CEE8"),
                padding=ft.Padding.only(left=13, top=6, bottom=10)
            )
        ]
        for grupo, opciones in grupos:
            controles.append(
                ft.Container(
                    content=ft.Text(grupo, size=10,
                                    weight=ft.FontWeight.BOLD, color="#80A5C8"),
                    padding=ft.Padding.only(left=13, top=17, bottom=8)
                )
            )
            for nombre, icono, accion in opciones:
                item = ft.Container(
                    content=ft.Row([
                        ft.Icon(getattr(ft.Icons, icono, ft.Icons.CIRCLE_OUTLINED),
                                size=17, color="#C8D9E9"),
                        ft.Text(nombre, size=12, color="#D6E5F4", expand=True,
                                weight=ft.FontWeight.W_500)
                    ], spacing=11),
                    padding=ft.Padding.symmetric(horizontal=13, vertical=10),
                    bgcolor=AZUL_OSCURO,
                    border_radius=10,
                    on_click=lambda e, n=nombre, f=accion: self._ir_a(n, f),
                    ink=True
                )
                self._nav_items[nombre] = item
                controles.append(item)

        controles += [
            ft.Container(height=16),
            ft.Text("DAO 2026   •   UTN FRC", size=10, color="#89AACA")
        ]
        menu = ft.Container(
            bgcolor=AZUL_OSCURO, width=254,
            padding=ft.Padding.symmetric(horizontal=15, vertical=17),
            content=ft.Column(
                controls=controles, spacing=2, scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        )
        self._actualizar_nav()

        cuerpo = ft.Row(
            controls=[
                menu,
                ft.Container(
                    content=self._contenido,
                    padding=ft.Padding.symmetric(horizontal=27, vertical=24),
                    expand=True
                )
            ],
            spacing=0, expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )
        self._page.add(
            ft.Column([encabezado, cuerpo], spacing=0, expand=True)
        )

    def _actualizar_nav(self):
        for nombre, item in self._nav_items.items():
            activo = nombre == self._pagina_activa
            item.bgcolor = "#214C78" if activo else AZUL_OSCURO
            icono, etiqueta = item.content.controls
            icono.color = "#FFFFFF" if activo else "#9FBAD5"
            etiqueta.color = "#FFFFFF" if activo else "#D1E0EF"
            etiqueta.weight = (
                ft.FontWeight.BOLD if activo else ft.FontWeight.W_500
            )

    def _ir_a(self, nombre, accion):
        self._pagina_activa = nombre
        self._actualizar_nav()
        accion()

    def _post(self):
        modernizar(self._contenido, self._page)
        self._page.update()

    def _mostrar_inicio(self, e=None):
        sedes = consultar_sedes()
        socios = consultar_socios()
        prestamos = consultar_prestamos()
        reservas = consultar_reservas()
        activos = sum(s[5] == 1 for s in sedes)
        prestamos_activos = sum(p[8] == "Activo" for p in prestamos)
        reservas_pendientes = sum(r[5] == "Pendiente" for r in reservas)

        def metrica(titulo, valor, subtitulo, icono):
            return ft.Container(
                width=236, bgcolor="#FFFFFF",
                border=ft.Border.all(1, BORDE), border_radius=16, padding=22,
                content=ft.Column([
                    ft.Row([
                        ft.Text(titulo, size=12, color=APAGADO, expand=True),
                        ft.Icon(getattr(ft.Icons, icono, ft.Icons.CIRCLE_OUTLINED),
                                color=AZUL, size=21),
                    ]),
                    ft.Text(str(valor), size=35, weight=ft.FontWeight.BOLD,
                            color=TINTA),
                    ft.Text(subtitulo, size=11, color=APAGADO)
                ], spacing=7)
            )

        accesos = [
            ("Nueva solicitud", "Solicitudes de préstamo",
             self._mostrar_solicitudes, "DESCRIPTION_OUTLINED"),
            ("Gestionar reservas", "Reservas y disponibilidad",
             self._mostrar_reservas, "EVENT_AVAILABLE_OUTLINED"),
            ("Consultar inventario", "Inventario por códigos",
             self._mostrar_inventario, "INVENTORY_2_OUTLINED"),
            ("Generar reportes", "Reportes",
             self._mostrar_reportes, "BAR_CHART_OUTLINED"),
        ]
        botones = [
            ft.Container(
                bgcolor="#F6F9FD",
                border_radius=11,
                border=ft.Border.all(1, BORDE),
                padding=15,
                width=218,
                ink=True,
                on_click=lambda e, n=seccion, f=accion: self._ir_a(n, f),
                content=ft.Column([
                    ft.Icon(getattr(ft.Icons, icono, ft.Icons.CIRCLE_OUTLINED),
                            color=AZUL, size=25),
                    ft.Text(nombre, color=TINTA,
                            weight=ft.FontWeight.W_500, size=13)
                ], spacing=12)
            ) for nombre, seccion, accion, icono in accesos
        ]

        self._contenido.controls = [
            ft.Column([
                ft.Text("Panel general", size=28, weight=ft.FontWeight.BOLD,
                        color=TINTA),
                ft.Text("Una vista clara del estado de BiblioRed.",
                        size=13, color=APAGADO),
            ], spacing=4),
            ft.Row([
                metrica("Sedes activas", activos,
                        f"{len(sedes)} sedes registradas", "ACCOUNT_BALANCE_OUTLINED"),
                metrica("Socios", len(socios),
                        "Personas registradas", "PEOPLE_OUTLINE_ROUNDED"),
                metrica("Préstamos activos", prestamos_activos,
                        "Ejemplares en circulación", "AUTO_STORIES_OUTLINED"),
                metrica("Reservas pendientes", reservas_pendientes,
                        "Solicitudes en espera", "EVENT_AVAILABLE_OUTLINED"),
            ], spacing=13, wrap=True),
            ft.Container(
                bgcolor="#FFFFFF", border_radius=16,
                border=ft.Border.all(1, BORDE), padding=24,
                content=ft.Column([
                    ft.Text("Accesos rápidos", size=19,
                            weight=ft.FontWeight.BOLD, color=TINTA),
                    ft.Text("Continuá con una tarea frecuente.",
                            size=12, color=APAGADO),
                    ft.Row(botones, spacing=14, wrap=True)
                ], spacing=14)
            ),
            ft.Container(
                bgcolor="#EAF2FF", border_radius=15, padding=22,
                content=ft.Row([
                    ft.Icon(ft.Icons.VERIFIED_OUTLINED, color=AZUL, size=28),
                    ft.Column([
                        ft.Text("Sistema de préstamos interbibliotecarios",
                                size=15, color=TINTA,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("Administrá el catálogo, los traslados, las reservas "
                                "y los préstamos desde un mismo lugar.",
                                size=12, color=APAGADO)
                    ], spacing=5)
                ], spacing=16)
            )
        ]
        self._post()

    def _mostrar_sedes(self, e=None):
        super()._mostrar_sedes(e)
        self._post()

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

        self._post()

    def _mostrar_catalogo(self, e=None):
        pantalla = VentanaCatalogo(self._page)

        self._contenido.controls = [
            self._crear_titulo(
                "Catálogo y ejemplares",
                "Administrá los libros y sus copias físicas por sede"
            ),
            pantalla.crear_contenido()
        ]

        self._post()

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

        self._post()

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

        self._post()

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

        self._post()

    def _mostrar_devoluciones(self, e=None):
        pantalla = VentanaDevoluciones(self._page)

        self._contenido.controls = [
            self._crear_titulo(
                "Devoluciones",
                "Estado físico, cierre de préstamos y retorno de ejemplares"
            ),
            pantalla.crear_contenido()
        ]

        self._post()

    def _mostrar_reservas(self, e=None):
        pantalla = VentanaReservas(self._page)

        self._contenido.controls = [
            self._crear_titulo(
                "Reservas y disponibilidad",
                "Consulta de ejemplares y gestión de reservas por sede"
            ),
            pantalla.crear_contenido()
        ]

        self._post()

    def _mostrar_inventario(self, e=None):
        pantalla = VentanaConsultas(self._page)
        self._contenido.controls = [
            self._crear_titulo("Inventario por códigos",
                              "Consulta de ejemplares, sede propietaria y ubicación"),
            pantalla.crear_inventario()
        ]
        self._post()

    def _mostrar_historial_lecturas(self, e=None):
        pantalla = VentanaConsultas(self._page)
        self._contenido.controls = [
            self._crear_titulo("Historial de lecturas",
                              "Préstamos y devoluciones por socio"),
            pantalla.crear_historial()
        ]
        self._post()

    def _mostrar_reportes(self, e=None):
        pantalla = VentanaConsultas(self._page)
        self._contenido.controls = [
            self._crear_titulo("Reportes de BiblioRed",
                              "Cuatro informes definidos en el PDF entregado"),
            pantalla.crear_reportes()
        ]
        self._post()
