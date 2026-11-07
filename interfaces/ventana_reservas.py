
import flet as ft
from interfaces.ui_moderno import icono_accion
from interfaces.ui_moderno import modernizar, normalizar

from servicios.reservas_servicio import ReservasServicio


class VentanaReservas:

    def __init__(self, page):
        self._page = page
        self._servicio = ReservasServicio()

        self._azul = "#153D63"
        self._celeste = "#63BDEB"
        self._seccion = "disponibilidad"

    def crear_contenido(self):
        self._zona = ft.Column(
            controls=[],
            spacing=15
        )

        self._dibujar()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Button(
                            "Consultar disponibilidad",
                            on_click=lambda e: self._cambiar("disponibilidad"),
                            bgcolor="#BCE7FF",
                            color=self._azul
                        ),
                        ft.Button(
                            "Gestionar reservas",
                            on_click=lambda e: self._cambiar("reservas"),
                            bgcolor="#BCE7FF",
                            color=self._azul
                        )
                    ],
                    spacing=10,
                    wrap=True
                ),
                self._zona
            ],
            spacing=16
        )

    def _cambiar(self, seccion):
        self._seccion = seccion
        self._dibujar()
        self._page.update()

    def _dibujar(self):
        if self._seccion == "disponibilidad":
            self._zona.controls = [
                self._vista_disponibilidad()
            ]
        else:
            self._zona.controls = [
                self._vista_reservas()
            ]
        modernizar(self._zona, self._page)

    def _mensaje(self, titulo, texto):
        dialogo = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(texto),
            actions=[
                ft.TextButton(
                    "Aceptar",
                    on_click=lambda e: self._page.pop_dialog()
                )
            ]
        )

        self._page.show_dialog(dialogo)

    def _vista_disponibilidad(self):
        self._filtro = ft.TextField(
            label="Buscar por título o ISBN",
            hint_text="Escribí una letra, un número o parte del título...",
            width=310,
            on_change=self._buscar,
            on_submit=self._buscar
        )

        sedes = self._servicio.listar_sedes_activas()

        self._filtro_sede = ft.Dropdown(
            label="Sede",
            width=230,
            value="todas",
            on_select=self._buscar,
            options=[
                ft.DropdownOption(
                    key="todas",
                    text="Todas las sedes"
                )
            ] + [
                ft.DropdownOption(
                    key=str(s[0]),
                    text=s[1]
                )
                for s in sedes
            ]
        )

        self._resultados = ft.Column(
            controls=[],
            spacing=10
        )

        self._actualizar_disponibilidad()

        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Disponibilidad por sede",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Los ejemplares disponibles pueden solicitarse "
                        "desde su sede propietaria.",
                        size=12,
                        color="#678197"
                    ),
                    ft.Row(
                        controls=[
                            self._filtro,
                            self._filtro_sede,
                            ft.Button(
                                "Buscar",
                                on_click=self._buscar,
                                bgcolor=self._celeste,
                                color=self._azul
                            )
                        ],
                        spacing=10,
                        wrap=True
                    ),
                    self._resultados
                ],
                spacing=16
            )
        )

    def _buscar(self, e):
        self._actualizar_disponibilidad()
        self._page.update()

    def _actualizar_disponibilidad(self):
        filtro = normalizar(self._filtro.value)
        filtro_sede = self._filtro_sede.value or "todas"

        tarjetas = []

        for datos in self._servicio.listar_disponibilidad():

            id_libro, titulo, isbn, id_sede, sede, copias, disponibles, pendientes = datos

            if filtro not in normalizar(titulo) and filtro not in normalizar(isbn):
                continue

            if filtro_sede != "todas" and filtro_sede != str(id_sede):
                continue

            tarjetas.append(
                ft.Container(
                    bgcolor="#F1F7FC",
                    border_radius=10,
                    padding=14,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                titulo,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=self._azul
                            ),
                            ft.Text(
                                f"ISBN: {isbn} · Sede: {sede}",
                                size=12
                            ),
                            ft.Text(
                                f"Ejemplares en la sede: {copias}  |  "
                                f"Disponibles: {disponibles}  |  "
                                f"Reservas pendientes: {pendientes}",
                                size=12
                            )
                        ],
                        spacing=5
                    )
                )
            )

        if not tarjetas:
            tarjetas.append(
                ft.Text(
                    "No hay resultados para los filtros seleccionados.",
                    color="#678197"
                )
            )

        self._resultados.controls = tarjetas

    def _vista_reservas(self):
        socios = self._servicio.listar_socios_habilitados()
        libros = self._servicio.listar_libros()
        sedes = self._servicio.listar_sedes_activas()

        self._socio = ft.Dropdown(
            label="Socio habilitado",
            options=[
                ft.DropdownOption(
                    key=str(s[0]),
                    text=f"{s[3]}, {s[2]} - DNI {s[1]}"
                )
                for s in socios
            ]
        )

        self._libro = ft.Dropdown(
            label="Título a reservar",
            options=[
                ft.DropdownOption(
                    key=str(l[0]),
                    text=f"{l[2]} - {l[1]}"
                )
                for l in libros
            ]
        )

        self._sede = ft.Dropdown(
            label="Biblioteca donde lo retirará",
            options=[
                ft.DropdownOption(
                    key=str(s[0]),
                    text=s[1]
                )
                for s in sedes
            ]
        )

        formulario = ft.Container(
            width=335,
            bgcolor="white",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Nueva reserva",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "La reserva es de un título, "
                        "no de una copia específica.",
                        size=12,
                        color="#678197"
                    ),
                    self._socio,
                    self._libro,
                    self._sede,
                    ft.Button(
                        "Registrar reserva",
                        on_click=self._guardar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=not socios or not libros or not sedes
                    )
                ],
                spacing=14
            )
        )

        tarjetas = []

        for r in self._servicio.listar_reservas():

            def atender(e, nro=r[0]):
                self._confirmar(nro, "atender")

            def cancelar(e, nro=r[0]):
                self._confirmar(nro, "cancelar")

            acciones = []

            if r[5] == "Pendiente":
                acciones = [
                    icono_accion("atender", "Atender reserva", atender),
                    icono_accion("cancelar", "Cancelar reserva", cancelar)
                ]

            texto_solicitud = (
                f" · Solicitud N.º {r[7]}"
                if r[7] is not None
                else ""
            )

            tarjetas.append(
                ft.Container(
                    bgcolor="#F1F7FC",
                    border_radius=10,
                    padding=14,
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        f"Reserva N.º {r[0]}",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=self._azul
                                    ),
                                    ft.Text(
                                        r[5],
                                        size=12,
                                        color=self._azul
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Text(
                                f"Socio: {r[1]} - DNI {r[2]}",
                                size=12
                            ),
                            ft.Text(
                                f"Título: {r[3]}",
                                size=12
                            ),
                            ft.Text(
                                f"Sede: {r[4]}{texto_solicitud}",
                                size=12
                            ),
                            ft.Row(
                                controls=acciones,
                                spacing=8,
                                wrap=True
                            )
                        ],
                        spacing=7
                    )
                )
            )

        if not tarjetas:
            tarjetas.append(
                ft.Text(
                    "Todavía no hay reservas registradas.",
                    color="#678197"
                )
            )

        listado = ft.Container(
            bgcolor="white",
            border_radius=12,
            padding=18,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Reservas registradas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Column(
                        controls=tarjetas,
                        spacing=12
                    )
                ],
                spacing=14
            )
        )

        return ft.Row(
            controls=[
                formulario,
                listado
            ],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _guardar(self, e):
        if (
            not self._socio.value
            or not self._libro.value
            or not self._sede.value
        ):
            self._mensaje(
                "Datos incompletos",
                "Seleccioná socio, título y sede."
            )
            return

        try:
            numero = self._servicio.registrar(
                int(self._socio.value),
                int(self._libro.value),
                int(self._sede.value)
            )

        except ValueError as error:
            self._mensaje(
                "No se pudo registrar",
                str(error)
            )
            return

        self._dibujar()
        self._page.update()

        self._mensaje(
            "Reserva registrada",
            f"Se creó la reserva N.º {numero}. Estado: Pendiente."
        )

    def _confirmar(self, id_reserva, operacion):
        texto = (
            "¿Querés atender esta reserva y generar la solicitud de préstamo correspondiente?"
            if operacion == "atender"
            else "¿Querés cancelar esta reserva?"
        )

        def confirmar(e):
            self._page.pop_dialog()

            try:
                if operacion == "atender":
                    numero = self._servicio.atender(id_reserva)

                    mensaje = (
                        f"Reserva atendida. Se creó la solicitud "
                        f"N.º {numero}. Si necesita traslado, avanzá desde "
                        "Remitos y traslados. La entrega se confirma en "
                        "Préstamos efectivos."
                    )

                else:
                    self._servicio.cancelar(id_reserva)
                    mensaje = (
                        "La reserva fue cancelada correctamente."
                    )

            except ValueError as error:
                self._mensaje(
                    "No se pudo completar",
                    str(error)
                )
                return

            self._dibujar()
            self._page.update()

            self._mensaje(
                "Operación realizada",
                mensaje
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar operación"),
            content=ft.Text(texto),
            actions=[
                ft.TextButton(
                    "Volver",
                    on_click=lambda e: self._page.pop_dialog()
                ),
                ft.Button(
                    "Confirmar",
                    on_click=confirmar
                )
            ]
        )

        self._page.show_dialog(dialogo)
