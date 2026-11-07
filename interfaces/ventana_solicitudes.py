
import flet as ft
from interfaces.ui_moderno import icono_accion

from servicios.prestamos_servicio import PrestamosServicio


class VentanaSolicitudes:

    def __init__(self, page, actualizar_pantalla):
        self._page = page
        self._actualizar_pantalla = actualizar_pantalla
        self._servicio = PrestamosServicio()
        self._azul = "#153D63"
        self._celeste = "#63BDEB"

    def crear_contenido(self):
        socios = self._servicio.listar_socios_habilitados()
        sedes = self._servicio.listar_sedes_activas()
        ejemplares = self._servicio.listar_ejemplares_disponibles()

        self._socio = ft.Dropdown(
            label="Socio habilitado",
            width=305,
            options=[
                ft.DropdownOption(
                    key=str(s[0]),
                    text=f"{s[3]}, {s[2]} - DNI {s[1]}"
                )
                for s in socios
            ]
        )

        self._ejemplar = ft.Dropdown(
            label="Ejemplar disponible (origen)",
            width=305,
            options=[
                ft.DropdownOption(
                    key=str(e[0]),
                    text=f"{e[1]} - {e[2]} - {e[4]}"
                )
                for e in ejemplares
            ]
        )

        self._destino = ft.Dropdown(
            label="Sede destino",
            width=305,
            options=[
                ft.DropdownOption(
                    key=str(s[0]),
                    text=s[1]
                )
                for s in sedes
            ]
        )

        formulario = ft.Container(
            width=345,
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Nueva solicitud",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Elegí un socio, una copia disponible y la "
                        "biblioteca donde quiere recibirla.",
                        size=12,
                        color="#678197"
                    ),
                    self._socio,
                    self._ejemplar,
                    self._destino,
                    ft.Text(
                        "La sede origen es la que tiene el ejemplar. "
                        "Si origen y destino coinciden, la solicitud "
                        "es local; si no, es interbibliotecaria.",
                        size=11,
                        color="#678197"
                    ),
                    ft.Button(
                        "Registrar solicitud",
                        on_click=self._guardar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=(
                            len(socios) == 0
                            or len(ejemplares) == 0
                            or len(sedes) == 0
                        )
                    )
                ],
                spacing=15
            )
        )

        tarjetas = []
        for datos in self._servicio.listar_solicitudes():
            puede_cancelar = datos[8] in (
                "Pendiente", "Pendiente de traslado"
            )

            def cancelar(e, numero=datos[0]):
                self._confirmar_cancelacion(numero)

            tarjetas.append(
                ft.Container(
                    bgcolor="#F1F7FC", padding=14, border_radius=11,
                    content=ft.Column([
                        ft.Text(
                            f"Solicitud N.º {datos[0]}",
                            weight=ft.FontWeight.BOLD, size=15,
                            color=self._azul
                        ),
                        ft.Text(
                            f"Estado: {datos[8]}", size=12, color="#59758B"
                        ),
                        ft.Text(f"Socio: {datos[1]}  ·  Ejemplar: {datos[3]}",
                                size=12),
                        ft.Text(f"Origen: {datos[5]}  ·  Destino: {datos[6]}",
                                size=12, color="#59758B"),
                        ft.Text(
                            f"Tipo: {datos[7]}", size=12, color="#59758B"
                        ),
                        ft.Row([
                            icono_accion(
                                "cancelar", "Cancelar solicitud",
                                cancelar, disabled=not puede_cancelar
                            )
                        ], spacing=8)
                    ], spacing=8)
                )
            )

        tarjetas_listado = ft.Column(
            controls=tarjetas or [
                ft.Text("Todavía no hay solicitudes registradas.",
                        color="#678197")
            ],
            spacing=10
        )

        listado = ft.Container(
            bgcolor="#FFFFFF",
            padding=18,
            border_radius=12,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Solicitudes registradas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    tarjetas_listado
                ],
                spacing=15
            )
        )

        return ft.Row(
            controls=[formulario, listado],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _crear_fila(self, datos):
        # Solo se puede cancelar una solicitud pendiente.
        puede_cancelar = datos[8] in (
            "Pendiente", "Pendiente de traslado"
        )

        def cancelar(e):
            self._confirmar_cancelacion(datos[0])

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(datos[0]))),
                ft.DataCell(ft.Text(datos[1])),
                ft.DataCell(ft.Text(datos[3])),
                ft.DataCell(ft.Text(datos[5])),
                ft.DataCell(ft.Text(datos[6])),
                ft.DataCell(ft.Text(datos[7])),
                ft.DataCell(ft.Text(datos[8])),
                ft.DataCell(
                    icono_accion(
                        "cancelar", "Cancelar solicitud",
                        cancelar, disabled=not puede_cancelar
                    )
                )
            ]
        )

    def _mensaje(self, titulo, mensaje):
        dialogo = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton(
                    "Aceptar",
                    on_click=lambda e: self._page.pop_dialog()
                )
            ]
        )

        self._page.show_dialog(dialogo)

    def _guardar(self, e):
        if (
            not self._socio.value
            or not self._ejemplar.value
            or not self._destino.value
        ):
            self._mensaje(
                "Datos incompletos",
                "Seleccioná el socio, el ejemplar y la sede destino."
            )
            return

        try:
            tipo = self._servicio.registrar(
                int(self._socio.value),
                int(self._ejemplar.value),
                int(self._destino.value)
            )

        except ValueError as error:
            self._mensaje(
                "No se pudo registrar",
                str(error)
            )
            return

        self._actualizar_pantalla()

        self._mensaje(
            "Solicitud registrada",
            "Se creó una solicitud de tipo " + tipo + ". "
            "El ejemplar ahora figura como Solicitado. "
            "Todavía no se realizó el préstamo ni el traslado."
        )

    def _confirmar_cancelacion(self, id_solicitud):

        def confirmar(e):
            self._page.pop_dialog()

            try:
                self._servicio.cancelar(id_solicitud)

            except ValueError as error:
                self._mensaje(
                    "No se pudo cancelar",
                    str(error)
                )
                return

            self._actualizar_pantalla()

            self._mensaje(
                "Solicitud cancelada",
                "Se canceló la solicitud y el ejemplar "
                "volvió a estar disponible."
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cancelar solicitud"),
            content=ft.Text(
                "¿Querés cancelar esta solicitud y liberar el ejemplar?"
            ),
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
