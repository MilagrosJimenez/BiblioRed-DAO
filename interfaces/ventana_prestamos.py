
from datetime import date
import flet as ft
from interfaces.ui_moderno import icono_accion

from servicios.prestamos_efectivos_servicio import PrestamosEfectivosServicio


class VentanaPrestamos:

    def __init__(self, page, actualizar_pantalla):
        self._page = page
        self._actualizar_pantalla = actualizar_pantalla
        self._servicio = PrestamosEfectivosServicio()

        self._azul = "#153D63"
        self._celeste = "#63BDEB"

    def crear_contenido(self):
        solicitudes = self._servicio.listar_solicitudes_listas()

        self._solicitud = ft.Dropdown(
            label="Solicitud lista para entregar",
            options=[
                ft.DropdownOption(
                    key=str(s[0]),
                    text=f"N.º {s[0]} - {s[1]} - {s[2]} ({s[5]})"
                )
                for s in solicitudes
            ]
        )

        self._plazo = ft.Dropdown(
            label="Plazo del préstamo",
            value="14",
            options=[
                ft.DropdownOption(key="7", text="7 días"),
                ft.DropdownOption(key="14", text="14 días"),
                ft.DropdownOption(key="21", text="21 días")
            ]
        )

        formulario = ft.Container(
            width=340,
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Registrar entrega",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Se muestran solamente las solicitudes "
                        "listas para entregar al socio.",
                        size=12,
                        color="#678197"
                    ),
                    self._solicitud,
                    self._plazo,
                    ft.Text(
                        "La fecha de entrega se registra automáticamente. "
                        "El ejemplar pasará al estado Prestado.",
                        size=11,
                        color="#678197"
                    ),
                    ft.Button(
                        "Confirmar préstamo",
                        on_click=self._guardar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=len(solicitudes) == 0
                    )
                ],
                spacing=15
            )
        )

        tarjetas = []

        for prestamo in self._servicio.listar_prestamos():
            tarjetas.append(
                self._crear_tarjeta(prestamo)
            )

        if len(tarjetas) == 0:
            tarjetas.append(
                ft.Text(
                    "Todavía no hay préstamos efectivos.",
                    color="#678197"
                )
            )

        listado = ft.Container(
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=18,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Préstamos registrados",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Column(
                        controls=tarjetas,
                        spacing=12
                    )
                ],
                spacing=16
            )
        )

        return ft.Row(
            controls=[formulario, listado],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _crear_tarjeta(self, datos):
        estado = datos[8]

        if (
            estado == "Activo"
            and datos[7] < date.today().isoformat()
        ):
            estado = "Vencido"

        def ver(e):
            self._ver_detalles(datos)

        return ft.Container(
            bgcolor="#F1F7FC",
            border_radius=10,
            padding=15,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"Préstamo N.º {datos[0]}",
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
                        f"Socio: {datos[1]} - DNI {datos[2]}",
                        size=12
                    ),
                    ft.Text(
                        f"Ejemplar: {datos[3]} - {datos[4]}",
                        size=12
                    ),
                    ft.Text(
                        f"Sede de entrega: {datos[5]}",
                        size=12
                    ),
                    ft.Text(
                        "Entrega: " + self._formatear_fecha(datos[6])
                        + "  |  Vence: "
                        + self._formatear_fecha(datos[7]),
                        size=12
                    ),
                    icono_accion("ver", "Ver detalles del préstamo", ver)
                ],
                spacing=7
            )
        )

    def _formatear_fecha(self, texto):
        return date.fromisoformat(texto).strftime("%d/%m/%Y")

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
        if not self._solicitud.value or not self._plazo.value:
            self._mensaje(
                "Datos incompletos",
                "Seleccioná una solicitud y el plazo del préstamo."
            )
            return

        try:
            id_prestamo = self._servicio.registrar_entrega(
                int(self._solicitud.value),
                int(self._plazo.value)
            )

        except ValueError as error:
            self._mensaje(
                "No se pudo prestar",
                str(error)
            )
            return

        self._actualizar_pantalla()

        self._mensaje(
            "Préstamo registrado",
            f"Se registró el préstamo N.º {id_prestamo}. "
            "El ejemplar ahora figura como Prestado."
        )

    def _ver_detalles(self, datos):
        mensaje = (
            f"Préstamo N.º {datos[0]}\n"
            f"Socio: {datos[1]}\n"
            f"Documento: {datos[2]}\n"
            f"Ejemplar: {datos[3]} - {datos[4]}\n"
            f"Sede de entrega: {datos[5]}\n"
            f"Tipo de solicitud: {datos[9]}\n"
            f"Fecha de préstamo: {self._formatear_fecha(datos[6])}\n"
            f"Vencimiento: {self._formatear_fecha(datos[7])}\n"
            f"Estado: {datos[8]}"
        )

        self._mensaje("Datos del préstamo", mensaje)
