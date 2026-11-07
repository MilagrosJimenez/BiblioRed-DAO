
import flet as ft
from interfaces.ui_moderno import icono_accion

from clases.socio import Socio
from datos.base_datos import (
    consultar_socios,
    guardar_socio,
    actualizar_datos_socio,
    actualizar_estado_socio
)


class VentanaSocios:

    def __init__(self, page, actualizar_pantalla):
        self._page = page
        self._actualizar_pantalla = actualizar_pantalla
        self._editando_id = None
        self._azul = "#153D63"
        self._celeste = "#63BDEB"

    def crear_contenido(self):
        self._campo_documento = ft.TextField(label="Documento")
        self._campo_nombre = ft.TextField(label="Nombre")
        self._campo_apellido = ft.TextField(label="Apellido")
        self._campo_telefono = ft.TextField(label="Teléfono")
        self._campo_correo = ft.TextField(label="Correo (opcional)")

        self._titulo_formulario = ft.Text(
            "Nuevo socio",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self._azul
        )

        self._boton_guardar = ft.Button(
            "Guardar socio",
            on_click=self._guardar,
            bgcolor=self._celeste,
            color=self._azul
        )

        self._boton_cancelar = ft.TextButton(
            "Cancelar edición",
            on_click=self._cancelar_edicion,
            visible=False
        )

        formulario = ft.Container(
            width=315,
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    self._titulo_formulario,
                    self._campo_documento,
                    self._campo_nombre,
                    self._campo_apellido,
                    self._campo_telefono,
                    self._campo_correo,
                    self._boton_guardar,
                    self._boton_cancelar
                ],
                spacing=12
            )
        )

        filas = []

        for datos in consultar_socios():
            filas.append(self._crear_fila(datos))

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Documento")),
                ft.DataColumn(ft.Text("Apellido y nombre")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=filas,
            heading_row_color="#E4F2FC",
            column_spacing=17
        )

        contenido_listado = [
            ft.Text(
                "Socios registrados",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=self._azul
            )
        ]

        if len(filas) == 0:
            contenido_listado.append(
                ft.Text(
                    "Todavía no hay socios registrados.",
                    color="#678197"
                )
            )

        contenido_listado.append(
            ft.Row(
                controls=[tabla],
                scroll=ft.ScrollMode.AUTO
            )
        )

        listado = ft.Container(
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=18,
            expand=True,
            content=ft.Column(
                controls=contenido_listado,
                spacing=16
            )
        )

        return ft.Row(
            controls=[formulario, listado],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=16
        )

    def _crear_fila(self, datos):
        estado = "Habilitado" if datos[6] == 1 else "Inhabilitado"
        accion = "Inhabilitar" if datos[6] == 1 else "Habilitar"

        def ver(e):
            self._ver(datos)

        def editar(e):
            self._cargar_edicion(datos)

        def cambiar(e):
            self._cambiar_estado(datos)

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(datos[1])),
                ft.DataCell(
                    ft.Text(datos[3] + ", " + datos[2])
                ),
                ft.DataCell(ft.Text(estado)),
                ft.DataCell(
                    ft.Row(
                        controls=[
                            icono_accion("ver", "Ver detalles del socio", ver),
                            icono_accion("editar", "Editar socio", editar),
                            icono_accion(
                                "inhabilitar" if datos[6] == 1 else "habilitar",
                                accion + " socio", cambiar
                            )
                        ],
                        spacing=1
                    )
                )
            ]
        )

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

    def _guardar(self, e):
        documento = (self._campo_documento.value or "").strip()
        nombre = (self._campo_nombre.value or "").strip()
        apellido = (self._campo_apellido.value or "").strip()
        telefono = (self._campo_telefono.value or "").strip()
        correo = (self._campo_correo.value or "").strip()

        try:
            socio = Socio(
                self._editando_id,
                documento,
                nombre,
                apellido,
                telefono,
                correo
            )

        except ValueError as error:
            self._mensaje("Datos inválidos", str(error))
            return

        if self._editando_id is None:

            if not guardar_socio(socio):
                self._mensaje(
                    "Documento duplicado",
                    "Ya existe un socio con ese documento."
                )
                return

            mensaje = "El socio se registró correctamente."

        else:
            actualizar_datos_socio(socio)
            mensaje = "Los datos del socio se actualizaron correctamente."

        self._actualizar_pantalla()
        self._mensaje("Operación realizada", mensaje)

    def _ver(self, datos):
        estado = "Habilitado" if datos[6] == 1 else "Inhabilitado"

        texto = (
            f"Número de socio: {datos[0]}\n"
            f"Documento: {datos[1]}\n"
            f"Nombre: {datos[2]}\n"
            f"Apellido: {datos[3]}\n"
            f"Teléfono: {datos[4]}\n"
            f"Correo: {datos[5] if datos[5] else 'No informado'}\n"
            f"Estado: {estado}"
        )

        self._mensaje("Datos del socio", texto)

    def _cargar_edicion(self, datos):
        self._editando_id = datos[0]

        self._campo_documento.value = datos[1]
        self._campo_documento.read_only = True

        self._campo_nombre.value = datos[2]
        self._campo_apellido.value = datos[3]
        self._campo_telefono.value = datos[4]
        self._campo_correo.value = datos[5]

        self._titulo_formulario.value = "Modificar socio"
        self._boton_guardar.content = "Guardar cambios"
        self._boton_cancelar.visible = True

        self._page.update()

    def _cancelar_edicion(self, e=None):
        self._actualizar_pantalla()

    def _cambiar_estado(self, datos):
        if datos[6] == 1:
            texto = "¿Deseás inhabilitar a este socio?"
        else:
            texto = "¿Deseás habilitar nuevamente a este socio?"

        def confirmar(e):
            self._page.pop_dialog()

            socio = Socio(
                datos[0],
                datos[1],
                datos[2],
                datos[3],
                datos[4],
                datos[5],
                bool(datos[6])
            )

            if datos[6] == 1:
                socio.inhabilitar()
            else:
                socio.habilitar()

            actualizar_estado_socio(socio)
            self._actualizar_pantalla()

            self._mensaje(
                "Operación realizada",
                "El estado del socio se actualizó correctamente."
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar operación"),
            content=ft.Text(texto),
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