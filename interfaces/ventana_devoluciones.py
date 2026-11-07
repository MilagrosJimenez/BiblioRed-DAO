
import flet as ft
from interfaces.ui_moderno import icono_accion
from interfaces.ui_moderno import modernizar

from servicios.devoluciones_servicio import DevolucionesServicio


class VentanaDevoluciones:

    def __init__(self, page):
        self._page = page
        self._servicio = DevolucionesServicio()
        self._azul = "#153D63"
        self._celeste = "#63BDEB"
        self._seccion = "devoluciones"

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
                            "Registrar devolución",
                            on_click=lambda e: self._cambiar("devoluciones"),
                            bgcolor="#BCE7FF",
                            color=self._azul
                        ),
                        ft.Button(
                            "Remitos de regreso",
                            on_click=lambda e: self._cambiar("retornos"),
                            bgcolor="#BCE7FF",
                            color=self._azul
                        )
                    ],
                    spacing=12
                ),
                self._zona
            ],
            spacing=15
        )

    def _cambiar(self, seccion):
        self._seccion = seccion
        self._dibujar()
        self._page.update()

    def _dibujar(self):
        if self._seccion == "devoluciones":
            self._zona.controls = [self._vista_devoluciones()]
        else:
            self._zona.controls = [self._vista_retornos()]

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

    def _vista_devoluciones(self):
        prestamos = self._servicio.listar_prestamos_activos()

        self._prestamo = ft.Dropdown(
            label="Préstamo activo",
            options=[
                ft.DropdownOption(
                    key=str(p[0]),
                    text=f"N.º {p[0]} - {p[2]} - {p[1]}"
                )
                for p in prestamos
            ]
        )

        self._estado_fisico = ft.Dropdown(
            label="Estado físico del material",
            options=[
                ft.DropdownOption(
                    key="Bueno",
                    text="Bueno"
                ),
                ft.DropdownOption(
                    key="Dañado",
                    text="Dañado"
                )
            ]
        )

        self._observaciones = ft.TextField(
            label="Observaciones (opcional)",
            multiline=True,
            min_lines=2,
            max_lines=3
        )

        formulario = ft.Container(
            width=325,
            bgcolor="white",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Registrar devolución",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Seleccioná el préstamo y verificá "
                        "el estado físico del ejemplar.",
                        size=12,
                        color="#678197"
                    ),
                    self._prestamo,
                    self._estado_fisico,
                    self._observaciones,
                    ft.Button(
                        "Confirmar devolución",
                        on_click=self._guardar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=len(prestamos) == 0
                    ),
                    ft.Text(
                        "Si el ejemplar pertenece a otra sede, "
                        "quedará pendiente de retorno.",
                        size=11,
                        color="#678197"
                    )
                ],
                spacing=14
            )
        )

        tarjetas = []

        for d in self._servicio.listar_devoluciones():
            texto = (
                f"Préstamo N.º {d[4]} · {d[5]}\n"
                f"Ejemplar: {d[6]} - {d[7]}\n"
                f"Recibido en: {d[8]} · Tipo: {d[9]}\n"
                f"Estado físico: {d[2]} · Fecha: {d[1]}\n"
                f"Estado actual del ejemplar: {d[10]}"
            )

            if d[3]:
                texto += f"\nObservaciones: {d[3]}"

            tarjetas.append(
                ft.Container(
                    bgcolor="#F1F7FC",
                    border_radius=10,
                    padding=14,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"Devolución N.º {d[0]}",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=self._azul
                            ),
                            ft.Text(texto, size=12)
                        ],
                        spacing=8
                    )
                )
            )

        if not tarjetas:
            tarjetas.append(
                ft.Text(
                    "Todavía no hay devoluciones.",
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
                        "Devoluciones registradas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Column(
                        controls=tarjetas,
                        spacing=12
                    )
                ],
                spacing=15
            )
        )

        return ft.Row(
            controls=[formulario, listado],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _guardar(self, e):
        if not self._prestamo.value or not self._estado_fisico.value:
            self._mensaje(
                "Datos incompletos",
                "Seleccioná el préstamo y el estado físico."
            )
            return

        try:
            numero = self._servicio.registrar(
                int(self._prestamo.value),
                self._estado_fisico.value,
                self._observaciones.value or ""
            )

        except ValueError as error:
            self._mensaje(
                "No se pudo devolver",
                str(error)
            )
            return

        self._dibujar()
        self._page.update()

        self._mensaje(
            "Devolución registrada",
            f"Se registró la devolución N.º {numero}. "
            "El préstamo quedó cerrado y se actualizó "
            "el estado del ejemplar."
        )

    def _vista_retornos(self):
        pendientes = self._servicio.listar_pendientes_retorno()

        self._devolucion = ft.Dropdown(
            label="Devolución pendiente de retorno",
            options=[
                ft.DropdownOption(
                    key=str(d[0]),
                    text=(
                        f"N.º {d[0]} - {d[1]} - "
                        f"{d[3]} a {d[4]}"
                    )
                )
                for d in pendientes
            ]
        )

        formulario = ft.Container(
            width=325,
            bgcolor="white",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Preparar regreso",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Un ejemplar interbibliotecario vuelve "
                        "a su sede propietaria con un remito.",
                        size=12,
                        color="#678197"
                    ),
                    self._devolucion,
                    ft.Button(
                        "Empaquetar y generar remito",
                        on_click=self._empaquetar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=len(pendientes) == 0
                    ),
                    ft.Text(
                        "El ejemplar recién podrá volver a Disponible "
                        "después de llegar a origen en buen estado.",
                        size=11,
                        color="#678197"
                    )
                ],
                spacing=14
            )
        )

        tarjetas = []

        for r in self._servicio.listar_remitos_retorno():

            def historial(e, n=r[0]):
                self._ver_historial(n)

            def avanzar(e, n=r[0]):
                self._confirmar_avance(n)

            acciones = [
                icono_accion("historial", "Ver historial del retorno", historial)
            ]

            if r[6] != "Recibido":
                accion = (
                    "Despachar"
                    if r[6] == "Empaquetado"
                    else "Confirmar recepción"
                )

                acciones.append(
                    icono_accion(
                        "despachar" if r[6] == "Empaquetado" else "recibir",
                        accion + " del retorno", avanzar
                    )
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
                                        f"Remito de regreso N.º {r[0]}",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=self._azul
                                    ),
                                    ft.Text(
                                        r[6],
                                        size=12,
                                        color=self._azul
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Text(
                                f"Ejemplar: {r[2]} - {r[3]}",
                                size=12
                            ),
                            ft.Text(
                                f"Origen: {r[4]} · Destino: {r[5]}",
                                size=12
                            ),
                            ft.Text(
                                f"Estado físico al devolver: {r[7]}",
                                size=12
                            ),
                            ft.Row(
                                controls=acciones,
                                wrap=True
                            )
                        ],
                        spacing=8
                    )
                )
            )

        if not tarjetas:
            tarjetas.append(
                ft.Text(
                    "Todavía no hay remitos de regreso.",
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
                        "Retornos registrados",
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
            controls=[formulario, listado],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _empaquetar(self, e):
        if not self._devolucion.value:
            self._mensaje(
                "Sin selección",
                "Seleccioná una devolución pendiente."
            )
            return

        try:
            id_remito = self._servicio.empaquetar(
                int(self._devolucion.value)
            )

        except ValueError as error:
            self._mensaje(
                "No se pudo empaquetar",
                str(error)
            )
            return

        self._dibujar()
        self._page.update()

        self._mensaje(
            "Remito creado",
            f"Se creó el remito de regreso N.º {id_remito}."
        )

    def _ver_historial(self, id_remito):
        movimientos = self._servicio.consultar_historial(
            id_remito
        )

        texto = "\n".join(
            f"{fecha} - {estado} - {observacion}"
            for estado, fecha, observacion in movimientos
        )

        self._mensaje(
            f"Historial del retorno N.º {id_remito}",
            texto
        )

    def _confirmar_avance(self, id_remito):

        def confirmar(e):
            self._page.pop_dialog()

            try:
                estado_ejemplar = self._servicio.avanzar(
                    id_remito
                )

            except ValueError as error:
                self._mensaje(
                    "No se pudo avanzar",
                    str(error)
                )
                return

            self._dibujar()
            self._page.update()

            self._mensaje(
                "Movimiento registrado",
                f"Estado actual del ejemplar: {estado_ejemplar}."
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar movimiento"),
            content=ft.Text(
                "¿Confirmás el siguiente movimiento "
                "del remito de regreso?"
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._page.pop_dialog()
                ),
                ft.Button(
                    "Confirmar",
                    on_click=confirmar
                )
            ]
        )

        self._page.show_dialog(dialogo)
