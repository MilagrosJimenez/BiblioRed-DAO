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
from interfaces.busqueda_general import buscar_en_bibliored
from interfaces.diseno_pantallas import (
    ANCHO, centrar, preparar_formulario_sedes, preparar_formulario_socios,
    preparar_formulario_solicitudes, preparar_formulario_remitos,
    preparar_listado_tabla, preparar_listado_tarjetas,
)
from datos.prestamos_datos import consultar_solicitudes
from datos.remitos_datos import consultar_remitos


class VentanaCompleta(VentanaFlet):

    def _crear_estructura(self):
        self._page.window.width = 1280
        self._page.window.height = 740
        self._page.bgcolor = FONDO
        self._azul = TINTA
        self._celeste = AZUL
        self._nav_items = {}
        self._pagina_activa = "Inicio"
        self._modos = {}
        self._filtro_pendiente = None
        self._modulo_actual = None
        self._catalogo_inicial = None

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
            height=82,
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
                    padding=ft.Padding.symmetric(horizontal=18, vertical=13),
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
        if self._filtro_pendiente and self._pagina_activa != "Inicio":
            consulta = self._filtro_pendiente
            self._filtro_pendiente = None
            campo = self._encontrar_buscador(self._contenido)
            if campo is not None:
                campo.value = consulta
                if campo.on_change:
                    campo.on_change(None)
        self._page.update()

    @staticmethod
    def _encontrar_buscador(control):
        if control is None:
            return None
        if isinstance(control, ft.TextField) and control.label == "Buscar en esta lista":
            return control
        if isinstance(control, (ft.Row, ft.Column)):
            for hijo in control.controls:
                campo = VentanaCompleta._encontrar_buscador(hijo)
                if campo is not None:
                    return campo
        if isinstance(control, ft.Container):
            return VentanaCompleta._encontrar_buscador(control.content)
        return None

    def _abrir_resultado(self, resultado):
        nombre = resultado["destino"]
        if resultado["tipo"] == "Ejemplar":
            self._catalogo_inicial = "ejemplares"
        elif resultado["tipo"] == "Libro":
            self._catalogo_inicial = "libros"

        self._modos[nombre] = "consultar"
        self._filtro_pendiente = (self._buscador_general.value or "").strip()
        acciones = {
            "Administrar sedes": self._mostrar_sedes,
            "Administrar socios": self._mostrar_socios,
            "Catálogo y ejemplares": self._mostrar_catalogo,
            "Solicitudes de préstamo": self._mostrar_solicitudes,
            "Remitos y traslados": self._mostrar_remitos,
        }
        self._ir_a(nombre, acciones[nombre])

    def _filtrar_global(self, e=None):
        consulta = (self._buscador_general.value or "").strip()
        self._panel_actividad.visible = not bool(consulta)
        if not consulta:
            self._resultados_global.controls = []
            self._panel_resultados.visible = False
            self._panel_accesos.visible = True
        else:
            encontrados = buscar_en_bibliored(consulta, limite=4)
            self._panel_resultados.visible = True
            self._panel_accesos.visible = False
            self._resultado_resumen.value = (
                f"{len(encontrados)} resultados mostrados"
                if encontrados else "Sin coincidencias"
            )
            self._resultados_global.controls = [
                ft.Container(
                    bgcolor="#F5F9FD",
                    border=ft.Border.all(1, BORDE),
                    border_radius=9,
                    padding=ft.Padding.symmetric(horizontal=13, vertical=8),
                    on_click=lambda ev, dato=dato: self._abrir_resultado(dato),
                    ink=True,
                    content=ft.Row([
                        ft.Icon(ft.Icons.SEARCH, color=AZUL, size=17),
                        ft.Text(dato["tipo"], color=AZUL, size=11, width=72),
                        ft.Text(dato["titulo"], color=TINTA, size=13,
                                weight=ft.FontWeight.BOLD, expand=True,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(dato["detalle"], color=APAGADO, size=11,
                                width=285, max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=13, color=AZUL)
                    ], spacing=9)
                )
                for dato in encontrados
            ] or [
                ft.Text("No encontramos registros con ese texto.",
                        size=13, color=APAGADO)
            ]
        self._page.update()

    def _mostrar_inicio(self, e=None):
        self._contenido.scroll = None
        self._contenido.spacing = 12
        sedes = consultar_sedes()
        socios = consultar_socios()
        prestamos = consultar_prestamos()
        reservas = consultar_reservas()
        activos = sum(s[5] == 1 for s in sedes)
        prestamos_activos = sum(p[8] == "Activo" for p in prestamos)
        reservas_pendientes = sum(r[5] == "Pendiente" for r in reservas)

        def metrica(titulo, valor, subtitulo, icono):
            return ft.Container(
                width=226, bgcolor="#FFFFFF",
                border=ft.Border.all(1, BORDE), border_radius=13,
                padding=ft.Padding.symmetric(horizontal=17, vertical=13),
                content=ft.Column([
                    ft.Row([
                        ft.Text(titulo, size=12, color=APAGADO, expand=True),
                        ft.Icon(getattr(ft.Icons, icono, ft.Icons.INFO_OUTLINE),
                                size=19, color=AZUL),
                    ]),
                    ft.Text(str(valor), size=30, weight=ft.FontWeight.BOLD,
                            color=TINTA),
                    ft.Text(subtitulo, size=11, color=APAGADO)
                ], spacing=3)
            )

        self._buscador_general = ft.TextField(
            label="Buscar en todo BiblioRed",
            hint_text="Nombre, documento, sede, título, ISBN, ejemplar o remito…",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=12,
            border_color=BORDE,
            focused_border_color=AZUL,
            text_size=15,
            height=56,
            width=ANCHO,
            on_change=self._filtrar_global,
            on_submit=self._filtrar_global,
        )
        self._resultado_resumen = ft.Text("", color=APAGADO, size=11)
        self._resultados_global = ft.Column(spacing=5)
        self._panel_resultados = ft.Container(
            visible=False, width=ANCHO, bgcolor="#FFFFFF",
            border=ft.Border.all(1, BORDE), border_radius=13, padding=12,
            content=ft.Column([
                self._resultado_resumen, self._resultados_global
            ], spacing=6)
        )

        accesos = [
            ("Nueva solicitud", "Solicitudes de préstamo",
             self._mostrar_solicitudes, "DESCRIPTION_OUTLINED", "registrar"),
            ("Consultar sedes", "Administrar sedes",
             self._mostrar_sedes, "ACCOUNT_BALANCE_OUTLINED", "consultar"),
            ("Ver catálogo", "Catálogo y ejemplares",
             self._mostrar_catalogo, "MENU_BOOK_OUTLINED", "consultar"),
            ("Preparar remitos", "Remitos y traslados",
             self._mostrar_remitos, "LOCAL_SHIPPING_OUTLINED", "registrar"),
        ]

        botones = []
        for titulo, seccion, accion, icono, modo in accesos:
            def abrir(ev, n=seccion, f=accion, m=modo):
                self._modos[n] = m
                self._ir_a(n, f)

            botones.append(ft.Container(
                width=214, bgcolor="#F4F8FE", border_radius=10,
                border=ft.Border.all(1, BORDE),
                padding=ft.Padding.symmetric(horizontal=14, vertical=13),
                on_click=abrir, ink=True,
                content=ft.Row([
                    ft.Icon(getattr(ft.Icons, icono, ft.Icons.SEARCH),
                            size=21, color=AZUL),
                    ft.Text(titulo, size=13, color=TINTA,
                            weight=ft.FontWeight.W_500, expand=True)
                ], spacing=10)
            ))

        self._panel_accesos = ft.Container(
            width=ANCHO, bgcolor="#FFFFFF", border=ft.Border.all(1, BORDE),
            border_radius=13, padding=17,
            content=ft.Column([
                ft.Text("Accesos rápidos", size=18,
                        weight=ft.FontWeight.BOLD, color=TINTA),
                ft.Row(botones, spacing=12, wrap=False),
            ], spacing=13)
        )

        self._panel_actividad = self._crear_actividad_reciente()

        # El mismo panel ocupa un ancho estable en ventana normal y
        # permanece centrado al maximizar, sin quedar pegado a la izquierda.
        self._contenido.controls = [
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                    ft.Column([
                        ft.Text("Inicio", size=27, weight=ft.FontWeight.BOLD, color=TINTA),
                        ft.Text("Todo lo que necesitás para gestionar BiblioRed.",
                                color=APAGADO, size=13),
                    ], spacing=3),
                    self._buscador_general,
                    ft.Row([
                        metrica("Sedes activas", activos,
                                f"{len(sedes)} registradas", "ACCOUNT_BALANCE_OUTLINED"),
                        metrica("Socios", len(socios),
                                "Personas registradas", "PEOPLE_OUTLINE_ROUNDED"),
                        metrica("Préstamos activos", prestamos_activos,
                                "Ejemplares en circulación", "AUTO_STORIES_OUTLINED"),
                        metrica("Reservas pendientes", reservas_pendientes,
                                "Solicitudes en espera", "EVENT_AVAILABLE_OUTLINED"),
                    ], spacing=11, wrap=False),
                    self._panel_accesos,
                    self._panel_resultados,
                    self._panel_actividad,

                        ],
                        spacing=12,
                        width=ANCHO
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0
            )
        ]
        self._post()

    def _crear_actividad_reciente(self):
        solicitudes = consultar_solicitudes()[:3]
        remitos = consultar_remitos()[:3]

        def resumen(titulo, entradas):
            return ft.Container(
                width=438,
                padding=ft.Padding.symmetric(horizontal=13, vertical=9),
                bgcolor="#F6F9FE",
                border_radius=10,
                content=ft.Column([
                    ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD,
                            color=TINTA),
                    *(ft.Text(dato, size=12, color=APAGADO, max_lines=1,
                               overflow=ft.TextOverflow.ELLIPSIS)
                      for dato in entradas),
                ] if entradas else [
                    ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD,
                            color=TINTA),
                    ft.Text("Sin movimientos recientes", size=12,
                            color=APAGADO),
                ], spacing=5),
            )

        solicitudes_texto = [
            f"Solicitud #{r[0]} · {r[1]} · {r[8]}"
            for r in solicitudes
        ]
        remitos_texto = [
            f"Remito #{r[0]} · {r[1]} · {r[5]}"
            for r in remitos
        ]
        return ft.Container(
            width=ANCHO,
            bgcolor="#FFFFFF",
            border_radius=13,
            border=ft.Border.all(1, BORDE),
            padding=ft.Padding.symmetric(horizontal=17, vertical=13),
            content=ft.Column([
                ft.Row([
                    ft.Text("Actividad reciente", size=16,
                            weight=ft.FontWeight.BOLD, color=TINTA),
                    ft.Text("Últimos registros", size=11, color=APAGADO),
                ], spacing=12),
                ft.Row([
                    resumen("Solicitudes", solicitudes_texto),
                    resumen("Remitos", remitos_texto)
                ], spacing=12),
            ], spacing=9),
        )

    def _cambiar_modo(self, clave, modo):
        self._modos[clave] = modo
        if self._modulo_actual != clave:
            return
        contenido = self._modulo_formulario if modo == "registrar" else self._modulo_listado
        self._modulo_zona.controls = [
            centrar(contenido)
        ]
        for nombre, boton in self._modulo_botones.items():
            activo = nombre == modo
            boton.bgcolor = AZUL if activo else "#FFFFFF"
            boton.color = "#FFFFFF" if activo else TINTA
        self._page.update()

    def _presentar_modulo(self, clave, encabezado, fila, registrar, consultar):
        self._contenido.scroll = ft.ScrollMode.AUTO
        self._contenido.spacing = 16
        self._modulo_actual = clave
        self._modulo_formulario, self._modulo_listado = fila.controls
        self._modulo_formulario.width = ANCHO
        self._modulo_formulario.height = None
        self._modulo_formulario.expand = False
        self._modulo_listado.width = ANCHO
        self._modulo_listado.expand = False
        self._modulo_botones = {
            "registrar": ft.Button(registrar,
                                   on_click=lambda e: self._cambiar_modo(clave, "registrar")),
            "consultar": ft.Button(consultar,
                                   on_click=lambda e: self._cambiar_modo(clave, "consultar")),
        }
        self._modulo_zona = ft.Column(spacing=0)
        self._contenido.controls = [
            encabezado,
            ft.Row([
                self._modulo_botones["registrar"],
                self._modulo_botones["consultar"]
            ], spacing=12),
            self._modulo_zona
        ]
        self._cambiar_modo(clave, self._modos.get(clave, "consultar"))
        self._post()

    def _mostrar_sedes(self, e=None):
        super()._mostrar_sedes(e)
        encabezado, fila = self._contenido.controls
        formulario, listado = fila.controls
        preparar_formulario_sedes(formulario, self)
        preparar_listado_tabla(listado, [1, 3, 3, 2, 2], self._page)
        self._presentar_modulo(
            "Administrar sedes", encabezado, fila,
            "Registrar nueva sede", "Consultar sedes"
        )

    def _cargar_edicion(self, datos):
        super()._cargar_edicion(datos)
        self._cambiar_modo("Administrar sedes", "registrar")

    def _mostrar_socios(self, e=None):
        def actualizar():
            self._modos["Administrar socios"] = "consultar"
            self._mostrar_socios()

        pantalla = VentanaSocios(self._page, actualizar)
        vista = pantalla.crear_contenido()
        editar_original = pantalla._cargar_edicion

        def editar_y_mostrar(datos):
            editar_original(datos)
            self._cambiar_modo("Administrar socios", "registrar")

        pantalla._cargar_edicion = editar_y_mostrar
        preparar_formulario_socios(vista.controls[0], pantalla)
        preparar_listado_tabla(vista.controls[1], [2, 4, 2, 3], self._page)
        self._presentar_modulo(
            "Administrar socios",
            self._crear_titulo("Administrar socios",
                               "Gestioná los datos y estados de los socios"),
            vista,
            "Registrar nuevo socio", "Consultar socios"
        )

    def _mostrar_catalogo(self, e=None):
        self._contenido.scroll = ft.ScrollMode.AUTO
        self._contenido.spacing = 16
        pantalla = VentanaCatalogo(self._page)
        if self._catalogo_inicial:
            pantalla._seccion = self._catalogo_inicial
            self._catalogo_inicial = None
        self._contenido.controls = [
            self._crear_titulo("Catálogo y ejemplares",
                               "Libros y copias físicas de cada biblioteca"),
            pantalla.crear_contenido()
        ]
        self._post()

    def _mostrar_solicitudes(self, e=None):
        def actualizar():
            self._modos["Solicitudes de préstamo"] = "consultar"
            self._mostrar_solicitudes()

        pantalla = VentanaSolicitudes(self._page, actualizar)
        vista = pantalla.crear_contenido()
        preparar_formulario_solicitudes(vista.controls[0], pantalla)
        preparar_listado_tarjetas(vista.controls[1])
        self._presentar_modulo(
            "Solicitudes de préstamo",
            self._crear_titulo("Solicitudes de préstamo",
                               "Préstamos locales e interbibliotecarios"),
            vista,
            "Nueva solicitud", "Consultar solicitudes"
        )

    def _mostrar_remitos(self, e=None):
        def actualizar():
            self._modos["Remitos y traslados"] = "consultar"
            self._mostrar_remitos()

        pantalla = VentanaRemitos(self._page, actualizar)
        vista = pantalla.crear_contenido()
        preparar_formulario_remitos(vista.controls[0], pantalla)
        preparar_listado_tarjetas(vista.controls[1])
        self._presentar_modulo(
            "Remitos y traslados",
            self._crear_titulo("Remitos y traslados",
                               "Empaquetado, despacho, recepción e historial"),
            vista,
            "Preparar remito", "Consultar y gestionar remitos"
        )

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
