
import flet as ft
from interfaces.ui_moderno import icono_accion

from servicios.remitos_servicio import RemitosServicio


class VentanaRemitos:

    def __init__(self, page, actualizar_pantalla):
        self._page = page
        self._actualizar_pantalla = actualizar_pantalla
        self._servicio = RemitosServicio()

        self._azul = "#153D63"
        self._celeste = "#63BDEB"

    def crear_contenido(self):
        pendientes = self._servicio.listar_pendientes()

        self._solicitud = ft.Dropdown(
            label="Solicitud pendiente de traslado",
            options=[
                ft.DropdownOption(
                    key=str(datos[0]),
                    text=(
                        f"N.º {datos[0]} - {datos[1]} - "
                        f"{datos[3]} a {datos[4]}"
                    )
                )
                for datos in pendientes
            ]
        )

        formulario = ft.Container(
            width=325,
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Preparar y empaquetar",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Seleccioná una solicitud entre dos sedes. "
                        "Se generará un remito único para ese ejemplar.",
                        size=12,
                        color="#678197"
                    ),
                    self._solicitud,
                    ft.Button(
                        "Empaquetar y generar remito",
                        on_click=self._empaquetar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=len(pendientes) == 0
                    ),
                    ft.Text(
                        "El ejemplar no se prestará todavía. "
                        "Primero deberá despacharse y recibirse en destino.",
                        size=11,
                        color="#678197"
                    )
                ],
                spacing=16
            )
        )

        tarjetas = []

        for datos in self._servicio.listar_remitos():
            tarjetas.append(
                self._crear_tarjeta_remito(datos)
            )

        if len(tarjetas) == 0:
            tarjetas.append(
                ft.Text(
                    "Todavía no hay remitos registrados.",
                    color="#678197"
                )
            )

        listado = ft.Container(
            bgcolor="#FFFFFF",
            padding=18,
            border_radius=12,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Remitos registrados",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Column(
                        controls=tarjetas,
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO
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

    def _crear_tarjeta_remito(self, datos):
        id_remito = datos[0]
        estado = datos[5]

        def ver_historial(e):
            self._mostrar_historial(id_remito)

        def avanzar(e):
            self._confirmar_cambio(id_remito, estado)

        acciones = [
            icono_accion("historial", "Ver historial del remito", ver_historial)
        ]

        if estado == "Empaquetado":
            acciones.append(
                icono_accion("despachar", "Despachar remito", avanzar)
            )

        elif estado == "En tránsito":
            acciones.append(
                icono_accion("recibir", "Confirmar recepción del remito", avanzar)
            )

        return ft.Container(
            bgcolor="#F1F7FC",
            border_radius=10,
            padding=15,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"Remito N.º {id_remito}",
                                weight=ft.FontWeight.BOLD,
                                color=self._azul,
                                size=15
                            ),
                            ft.Text(
                                estado,
                                color=self._azul,
                                size=12
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text(
                        f"Ejemplar: {datos[1]} - {datos[2]}",
                        size=12
                    ),
                    ft.Text(
                        f"Origen: {datos[3]}",
                        size=12
                    ),
                    ft.Text(
                        f"Destino: {datos[4]}",
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

    def _empaquetar(self, e):
        if not self._solicitud.value:
            self._mensaje(
                "Datos incompletos",
                "Seleccioná una solicitud pendiente"
            )
            return

        try:
            id_remito = self._servicio.empaquetar(
                int(self._solicitud.value)
            )

        except ValueError as error:
            self._mensaje(
                "No se pudo empaquetar",
                str(error)
            )
            return

        self._actualizar_pantalla()

        self._mensaje(
            "Remito generado",
            f"Se generó el remito N.º {id_remito}. "
            "El ejemplar quedó empaquetado, "
            "pendiente de despacho."
        )

    def _mostrar_historial(self, id_remito):
        historial = self._servicio.ver_historial(
            id_remito
        )

        texto = ""

        for estado, fecha, observacion in historial:
            detalle = f" — {observacion}" if observacion else ""
            texto += f"{fecha} | {estado}{detalle}\n"

        if texto == "":
            texto = (
                "El remito todavía no tiene "
                "movimientos registrados."
            )

        self._mensaje(
            f"Historial del remito N.º {id_remito}",
            texto
        )

    def _confirmar_cambio(self, id_remito, estado):
        if estado == "Empaquetado":
            pregunta = (
                "¿Confirmás el despacho del ejemplar?"
            )

        elif estado == "En tránsito":
            pregunta = (
                "¿Confirmás que el ejemplar fue "
                "recibido en destino?"
            )

        else:
            return

        def confirmar(e):
            self._page.pop_dialog()

            try:
                nuevo_estado = self._servicio.cambiar_estado(
                    id_remito
                )

            except ValueError as error:
                self._mensaje(
                    "No se pudo actualizar",
                    str(error)
                )
                return

            self._actualizar_pantalla()

            self._mensaje(
                "Remito actualizado",
                f"Remito N.º {id_remito}: {nuevo_estado}. "
                "El movimiento quedó guardado en el historial."
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar movimiento"),
            content=ft.Text(pregunta),
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
