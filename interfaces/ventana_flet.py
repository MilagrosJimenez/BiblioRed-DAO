
import os
import flet as ft

from clases.sede import Sede
from datos.base_datos import (
    crear_tabla_sedes,
    guardar_sede,
    consultar_sedes,
    actualizar_estado_sede,
    actualizar_datos_sede
)


class VentanaFlet:

    def __init__(self, page):
        self._page = page
        self._azul = "#153D63"
        self._celeste = "#63BDEB"
        self._fondo = "#F1F7FC"

        self._dias = [
            "Lunes", "Martes", "Miércoles",
            "Jueves", "Viernes", "Sábado", "Domingo"
        ]

        self._horas = []
        for hora in range(24):
            for minuto in ("00", "30"):
                self._horas.append(f"{hora:02d}:{minuto}")
        self._horas.append("24:00")

        self._editando_id = None
        self._horario_anterior = ""

        crear_tabla_sedes()

        self._page.title = "BiblioRed - UTN FRC"
        self._page.window.width = 1200
        self._page.window.height = 780
        self._page.bgcolor = self._fondo
        self._page.padding = 0
        self._page.theme_mode = ft.ThemeMode.LIGHT

        self._contenido = ft.Column(
            controls=[],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        self._crear_estructura()
        self._mostrar_inicio()

    def _crear_logo(self):
        ruta = os.path.join(
            os.path.dirname(__file__),
            "..", "imagenes", "logo_utn.png"
        )

        if os.path.exists(ruta):
            with open(ruta, "rb") as archivo:
                imagen = archivo.read()

            return ft.Image(
                src=imagen,
                width=210,
                height=75,
                fit=ft.BoxFit.CONTAIN
            )

        return ft.Text(
            "UTN FRC",
            size=22,
            weight=ft.FontWeight.BOLD,
            color="#1736B3"
        )

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

        menu = ft.Container(
            bgcolor=self._azul,
            width=240,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "NAVEGACIÓN",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#B6D8EE"
                    ),
                    ft.Button(
                        "Inicio",
                        on_click=self._mostrar_inicio,
                        bgcolor="#BCE7FF",
                        color=self._azul,
                        width=195
                    ),
                    ft.Button(
                        "Administrar sedes",
                        on_click=self._mostrar_sedes,
                        bgcolor="#BCE7FF",
                        color=self._azul,
                        width=195
                    ),
                    ft.Container(height=15),
                    ft.Text(
                        "PRÓXIMAMENTE",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#B6D8EE"
                    ),
                    ft.Text("Socios", color="#D2E5F2"),
                    ft.Text("Catálogo y ejemplares", color="#D2E5F2"),
                    ft.Text("Préstamos y reservas", color="#D2E5F2"),
                    ft.Text("Envíos y devoluciones", color="#D2E5F2"),
                    ft.Text("Reportes", color="#D2E5F2"),
                    ft.Container(height=20),
                    ft.Text(
                        "DAO 2026 - UTN FRC",
                        size=11,
                        color="#A9C6DA"
                    )
                ],
                spacing=19
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
                controls=[encabezado, cuerpo],
                spacing=0,
                expand=True
            )
        )

    def _crear_titulo(self, titulo, descripcion):
        return ft.Column(
            controls=[
                ft.Text(
                    titulo,
                    size=27,
                    weight=ft.FontWeight.BOLD,
                    color=self._azul
                ),
                ft.Text(
                    descripcion,
                    size=13,
                    color="#678197"
                )
            ],
            spacing=5
        )

    def _crear_tarjeta(self, titulo, numero, descripcion):
        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=24,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        titulo,
                        size=13,
                        color="#678197"
                    ),
                    ft.Text(
                        str(numero),
                        size=34,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        descripcion,
                        size=11,
                        color="#7891A4"
                    )
                ],
                spacing=8
            )
        )

    def _mostrar_inicio(self, e=None):
        sedes = consultar_sedes()
        activas = 0

        for sede in sedes:
            if sede[5] == 1:
                activas += 1

        tarjetas = ft.Row(
            controls=[
                self._crear_tarjeta(
                    "Sedes registradas",
                    len(sedes),
                    "Total de bibliotecas"
                ),
                self._crear_tarjeta(
                    "Sedes activas",
                    activas,
                    "Habilitadas para operar"
                )
            ],
            spacing=15
        )

        bienvenida = ft.Container(
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=28,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Bienvenida a BiblioRed",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Administrá las bibliotecas de la red, "
                        "sus socios, libros y préstamos.",
                        size=14,
                        color="#59758B"
                    ),
                    ft.Button(
                        "Administrar sedes",
                        on_click=self._mostrar_sedes,
                        bgcolor=self._celeste,
                        color=self._azul
                    )
                ],
                spacing=18
            )
        )

        self._contenido.controls = [
            self._crear_titulo(
                "Panel principal",
                "Información general del sistema"
            ),
            tarjetas,
            bienvenida
        ]

        self._page.update()

    def _crear_selector(self, etiqueta, valores):
        return ft.Dropdown(
            label=etiqueta,
            width=135,
            options=[
                ft.DropdownOption(key=valor, text=valor)
                for valor in valores
            ],
            on_select=self._mostrar_vista_previa
        )

    def _mostrar_sedes(self, e=None):
        self._editando_id = None
        self._horario_anterior = ""

        self._campo_id = ft.TextField(label="ID", width=109)
        self._campo_nombre = ft.TextField(label="Nombre")
        self._campo_direccion = ft.TextField(label="Dirección")
        self._campo_telefono = ft.TextField(label="Teléfono", width=174)

        # SELECCIÓN DE DÍAS
        self._dia_desde = self._crear_selector(
            "Desde", self._dias
        )
        self._dia_hasta = self._crear_selector(
            "Hasta", self._dias
        )

        # SELECCIÓN DE HORARIOS
        self._hora_desde = self._crear_selector(
            "Desde", self._horas[:-1]
        )
        self._hora_hasta = self._crear_selector(
            "Hasta", self._horas[1:]
        )
        self._atencion_24h = ft.Checkbox(
            label="24 horas",
            value=False,
            on_change=self._cambiar_atencion_24h
        )

        self._vista_previa = ft.Text(
            "Seleccioná el rango de días y horas.",
            size=11,
            color="#678197"
        )

        self._horario_actual = ft.Text(
            "",
            size=11,
            color="#678197",
            visible=False
        )

        self._titulo_formulario = ft.Text(
            "Nueva sede",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self._azul
        )

        self._boton_guardar = ft.Button(
            "Guardar sede",
            on_click=self._guardar_sede,
            bgcolor=self._celeste,
            color=self._azul
        )

        self._boton_cancelar = ft.TextButton(
            "Cancelar edición",
            on_click=self._mostrar_sedes,
            visible=False
        )

        formulario = ft.Container(
            width=335,
            height=540,
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=18,
            content=ft.Column(
                controls=[
                    self._titulo_formulario,
                    ft.Row(
                        controls=[self._campo_id, self._campo_telefono],
                        spacing=8
                    ),
                    self._campo_nombre,
                    self._campo_direccion,
                    ft.Text(
                        "Días de atención",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Row(
                        controls=[
                            self._dia_desde,
                            self._dia_hasta
                        ],
                        spacing=8
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Horario de atención",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=self._azul
                            ),
                            self._atencion_24h
                        ],
                        spacing=9
                    ),
                    ft.Row(
                        controls=[
                            self._hora_desde,
                            self._hora_hasta
                        ],
                        spacing=8
                    ),
                    self._horario_actual,
                    self._vista_previa,
                    self._boton_guardar,
                    self._boton_cancelar
                ],
                spacing=7,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        )

        # LISTADO DE SEDES
        filas = []

        for sede in consultar_sedes():
            filas.append(self._crear_fila_sede(sede))

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=filas,
            column_spacing=12,
            heading_row_color="#E4F2FC"
        )

        listado = ft.Container(
            bgcolor="#FFFFFF",
            border_radius=12,
            padding=18,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Sedes registradas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Row(
                        controls=[tabla],
                        scroll=ft.ScrollMode.AUTO
                    )
                ],
                spacing=15
            )
        )

        self._contenido.controls = [
            self._crear_titulo(
                "Administrar sedes",
                "Registrá, modificá y consultá las bibliotecas"
            ),
            ft.Row(
                controls=[
                    formulario,
                    listado
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ]

        self._page.update()

    def _texto_horario(self):
        dia_inicio = self._dia_desde.value
        dia_fin = self._dia_hasta.value
        hora_inicio = self._hora_desde.value
        hora_fin = self._hora_hasta.value

        if self._atencion_24h.value:
            periodo = (dia_inicio if dia_inicio == dia_fin
                       else f"{dia_inicio} a {dia_fin.lower()}")
            return f"{periodo}: atención 24 horas"

        # La hora de cierre menor a la de apertura significa que el
        # turno termina el día siguiente (por ejemplo, 18:00 a 09:00).
        aclaracion = " (día siguiente)" if hora_fin < hora_inicio else ""

        if dia_inicio == dia_fin:
            return f"{dia_inicio} de {hora_inicio} a {hora_fin}{aclaracion}"

        # Los días son un rango semanal circular: viernes a lunes
        # también es válido.
        return (
            f"{dia_inicio} a {dia_fin.lower()} "
            f"de {hora_inicio} a {hora_fin}{aclaracion}"
        )

    def _cambiar_atencion_24h(self, e=None):
        es_24h = bool(self._atencion_24h.value)
        self._hora_desde.disabled = es_24h
        self._hora_hasta.disabled = es_24h
        self._mostrar_vista_previa()

    def _mostrar_vista_previa(self, e=None):
        dias_completos = bool(self._dia_desde.value and self._dia_hasta.value)
        horas_completas = bool(self._hora_desde.value and self._hora_hasta.value)

        if dias_completos and (self._atencion_24h.value or horas_completas):
            if not self._atencion_24h.value and self._hora_desde.value == self._hora_hasta.value:
                self._vista_previa.value = (
                    "Elegí horas distintas o marcá Atención 24 horas."
                )
            else:
                self._vista_previa.value = (
                    "Nuevo horario: " + self._texto_horario()
                )
        elif self._atencion_24h.value:
            self._vista_previa.value = "Seleccioná los días de atención."
        else:
            self._vista_previa.value = "Seleccioná el rango de días y horas."

        self._page.update()

    def _crear_fila_sede(self, datos):
        estado = "Activa" if datos[5] == 1 else "Dada de baja"

        if datos[5] == 1:
            texto_estado = "Dar de baja"
        else:
            texto_estado = "Reactivar"

        def ver(e):
            self._ver_detalles(datos)

        def editar(e):
            self._cargar_edicion(datos)

        def cambiar(e):
            self._cambiar_estado(datos)

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(datos[0]))),
                ft.DataCell(ft.Text(datos[1])),
                ft.DataCell(ft.Text(datos[2])),
                ft.DataCell(ft.Text(estado)),
                ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY_OUTLINED,
                                tooltip="Ver detalles de la sede",
                                icon_size=19,
                                width=36,
                                height=36,
                                on_click=ver
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar sede",
                                icon_size=19,
                                width=36,
                                height=36,
                                on_click=editar
                            ),
                            ft.IconButton(
                                icon=(ft.Icons.BLOCK_OUTLINED if datos[5] == 1
                                      else ft.Icons.CHECK_CIRCLE_OUTLINED),
                                tooltip=texto_estado,
                                icon_size=19,
                                width=36,
                                height=36,
                                on_click=cambiar
                            )
                        ],
                        spacing=0
                    )
                )
            ]
        )

    def _mostrar_mensaje(self, titulo, mensaje):
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

    def _guardar_sede(self, e):
        id_texto = (self._campo_id.value or "").strip()
        nombre = (self._campo_nombre.value or "").strip()
        direccion = (self._campo_direccion.value or "").strip()
        telefono = (self._campo_telefono.value or "").strip()

        if id_texto == "" or not id_texto.isnumeric():
            self._mostrar_mensaje(
                "Datos inválidos",
                "Ingresá un ID numérico válido."
            )
            return

        if nombre == "" or direccion == "" or telefono == "":
            self._mostrar_mensaje(
                "Datos incompletos",
                "Completá los datos de la sede."
            )
            return

        valores = (
            self._dia_desde.value,
            self._dia_hasta.value,
            self._hora_desde.value,
            self._hora_hasta.value
        )
        es_24h = bool(self._atencion_24h.value)
        era_24h = "24 horas" in self._horario_anterior

        # Conserva el horario anterior únicamente si no se seleccionó
        # ningún valor nuevo ni se cambió la modalidad 24 horas.
        if (self._editando_id is not None and not any(valores)
                and es_24h == era_24h):
            horarios = self._horario_anterior
        else:
            if not self._dia_desde.value or not self._dia_hasta.value:
                self._mostrar_mensaje(
                    "Horarios incompletos",
                    "Seleccioná los días de atención."
                )
                return

            if not es_24h:
                if not self._hora_desde.value or not self._hora_hasta.value:
                    self._mostrar_mensaje(
                        "Horarios incompletos",
                        "Seleccioná las horas de apertura y cierre."
                    )
                    return
                if self._hora_desde.value == self._hora_hasta.value:
                    self._mostrar_mensaje(
                        "Horario inválido",
                        "Las horas iguales son ambiguas. Para atención "
                        "continua, marcá la opción 24 horas."
                    )
                    return

            # Los días son un rango semanal circular y los turnos
            # nocturnos se indican como cierre al día siguiente.
            horarios = self._texto_horario()

        try:
            sede = Sede(
                int(id_texto),
                nombre,
                direccion,
                telefono,
                horarios
            )

        except ValueError as error:
            self._mostrar_mensaje(
                "Datos inválidos",
                str(error)
            )
            return

        if self._editando_id is None:
            if not guardar_sede(sede):
                self._mostrar_mensaje(
                    "ID duplicado",
                    "Ya existe una sede con ese identificador."
                )
                return

            mensaje = "La sede se registró correctamente."

        else:
            actualizar_datos_sede(sede)
            mensaje = (
                "Los datos de la sede se modificaron correctamente."
            )

        self._mostrar_sedes()
        self._mostrar_mensaje("Operación realizada", mensaje)

    def _ver_detalles(self, datos):
        estado = "Activa" if datos[5] == 1 else "Dada de baja"

        texto = (
            f"ID: {datos[0]}\n"
            f"Nombre: {datos[1]}\n"
            f"Dirección: {datos[2]}\n"
            f"Teléfono: {datos[3]}\n"
            f"Horarios: {datos[4]}\n"
            f"Estado: {estado}"
        )

        self._mostrar_mensaje("Datos de la sede", texto)

    def _cargar_edicion(self, datos):
        self._editando_id = datos[0]
        self._horario_anterior = datos[4]
        self._atencion_24h.value = "24 horas" in datos[4]
        self._hora_desde.disabled = bool(self._atencion_24h.value)
        self._hora_hasta.disabled = bool(self._atencion_24h.value)

        self._campo_id.value = str(datos[0])
        self._campo_id.read_only = True

        self._campo_nombre.value = datos[1]
        self._campo_direccion.value = datos[2]
        self._campo_telefono.value = datos[3]

        self._horario_actual.value = (
            "Horario actual: " + datos[4]
        )
        self._horario_actual.visible = True

        self._vista_previa.value = (
            "Para cambiar el horario, elegí un nuevo rango. "
            "Si no seleccionás nada, se conservará el actual."
        )

        self._titulo_formulario.value = "Modificar sede"
        self._boton_guardar.content = "Guardar cambios"
        self._boton_cancelar.visible = True

        self._page.update()

    def _cambiar_estado(self, datos):
        if datos[5] == 1:
            pregunta = "¿Deseás dar de baja esta sede?"
        else:
            pregunta = "¿Deseás reactivar esta sede?"

        def confirmar(e):
            self._page.pop_dialog()

            sede = Sede(
                datos[0],
                datos[1],
                datos[2],
                datos[3],
                datos[4]
            )

            if datos[5] == 1:
                sede.dar_de_baja()
            else:
                sede.reactivar()

            actualizar_estado_sede(sede)
            self._mostrar_sedes()

            self._mostrar_mensaje(
                "Operación realizada",
                "El estado se actualizó correctamente."
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar operación"),
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
