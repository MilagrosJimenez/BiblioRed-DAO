
import flet as ft
from interfaces.ui_moderno import icono_accion
from interfaces.ui_moderno import modernizar
from interfaces.diseno_pantallas import (
    ANCHO, centrar, preparar_formulario_catalogo,
    preparar_listado_tarjetas,
)

from servicios.catalogo_servicio import CatalogoServicio


class VentanaCatalogo:

    def __init__(self, page):
        self._page = page
        self._servicio = CatalogoServicio()
        self._azul = "#153D63"
        self._celeste = "#63BDEB"
        self._seccion = "libros"
        self._modo = "consultar"
        self._editando_id = None
        self._isbn_edicion = ""

    def crear_contenido(self):
        self._zona = ft.Column(controls=[], spacing=14)
        self._boton_libros = ft.Button(
            "Libros", on_click=lambda e: self._cambiar_seccion("libros")
        )
        self._boton_ejemplares = ft.Button(
            "Ejemplares físicos",
            on_click=lambda e: self._cambiar_seccion("ejemplares")
        )
        self._boton_registrar = ft.Button(
            "Registrar libro",
            on_click=lambda e: self._cambiar_modo("registrar")
        )
        self._boton_consultar = ft.Button(
            "Consultar libros",
            on_click=lambda e: self._cambiar_modo("consultar")
        )
        self._dibujar()
        return ft.Column([
            ft.Row([
                ft.Text("Sección", color="#667B93", size=12),
                self._boton_libros, self._boton_ejemplares
            ], spacing=10),
            ft.Row([
                self._boton_registrar, self._boton_consultar
            ], spacing=12),
            self._zona
        ], spacing=13)

    def _actualizar_botones(self):
        self._boton_registrar.content = (
            "Registrar libro" if self._seccion == "libros"
            else "Registrar ejemplar"
        )
        self._boton_consultar.content = (
            "Consultar libros" if self._seccion == "libros"
            else "Consultar ejemplares"
        )
        for boton, activo in (
            (self._boton_libros, self._seccion == "libros"),
            (self._boton_ejemplares, self._seccion == "ejemplares"),
            (self._boton_registrar, self._modo == "registrar"),
            (self._boton_consultar, self._modo == "consultar"),
        ):
            boton.bgcolor = "#2563EB" if activo else "#FFFFFF"
            boton.color = "#FFFFFF" if activo else "#142B49"

    def _cambiar_seccion(self, seccion):
        self._seccion = seccion
        self._modo = "consultar"
        self._editando_id = None
        self._dibujar()
        self._page.update()

    def _cambiar_modo(self, modo):
        self._modo = modo
        self._actualizar_botones()
        elegido = self._formulario if modo == "registrar" else self._listado
        self._zona.controls = [centrar(elegido)]
        self._page.update()

    def _dibujar(self):
        vista = (self._vista_libros() if self._seccion == "libros"
                 else self._vista_ejemplares())
        self._formulario, self._listado = vista.controls
        preparar_formulario_catalogo(self._formulario, self)
        preparar_listado_tarjetas(self._listado)
        self._actualizar_botones()
        elegido = self._formulario if self._modo == "registrar" else self._listado
        self._zona.controls = [centrar(elegido)]
        modernizar(self._zona, self._page)

    def _mensaje(self, titulo, descripcion):
        dialogo = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(descripcion),
            actions=[
                ft.TextButton(
                    "Aceptar",
                    on_click=lambda e: self._page.pop_dialog()
                )
            ]
        )

        self._page.show_dialog(dialogo)

    def _vista_libros(self):
        self._titulo_formulario = ft.Text(
            "Nuevo libro",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self._azul
        )

        self._isbn = ft.TextField(label="ISBN")
        self._titulo = ft.TextField(label="Título")
        self._autor = ft.TextField(label="Autor")
        self._editorial = ft.TextField(label="Editorial")

        self._boton_guardar = ft.Button(
            "Guardar libro",
            on_click=self._guardar_libro,
            bgcolor=self._celeste,
            color=self._azul
        )

        self._boton_cancelar = ft.TextButton(
            "Cancelar edición",
            on_click=lambda e: self._cambiar_seccion("libros"),
            visible=False
        )

        formulario = ft.Container(
            width=300,
            bgcolor="white",
            border_radius=12,
            padding=20,
            content=ft.Column(
                controls=[
                    self._titulo_formulario,
                    self._isbn,
                    self._titulo,
                    self._autor,
                    self._editorial,
                    self._boton_guardar,
                    self._boton_cancelar
                ],
                spacing=12
            )
        )

        tarjetas = []
        for datos in self._servicio.listar_libros():

            def editar(e, libro=datos):
                self._editar_libro(libro)

            def ver(e, libro=datos):
                self._ver_libro(libro)

            tarjetas.append(
                ft.Container(
                    bgcolor="#F1F7FC", padding=14, border_radius=11,
                    content=ft.Column([
                        ft.Text(
                            datos[2], size=15,
                            weight=ft.FontWeight.BOLD, color=self._azul
                        ),
                        ft.Text(
                            f"{datos[6]} disponibles / {datos[5]} copias",
                            size=11, color="#59758B"
                        ),
                        ft.Text(f"ISBN: {datos[1]}  ·  Autor: {datos[3]}",
                                size=12, color="#59758B"),
                        ft.Row([
                            icono_accion("ver", "Ver detalles del libro", ver),
                            icono_accion("editar", "Editar libro", editar)
                        ], spacing=6, wrap=True)
                    ], spacing=5)
                )
            )

        tarjetas_listado = ft.Column(
            controls=tarjetas or [
                ft.Text("Todavía no hay libros registrados.", color="#678197")
            ],
            spacing=10
        )

        listado = ft.Container(
            bgcolor="white",
            border_radius=12,
            padding=18,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Catálogo de libros",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    tarjetas_listado
                ],
                spacing=14
            )
        )

        return ft.Row(
            controls=[formulario, listado],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _guardar_libro(self, e):
        isbn = self._isbn.value or ""
        titulo = self._titulo.value or ""
        autor = self._autor.value or ""
        editorial = self._editorial.value or ""

        try:
            if self._editando_id is None:
                self._servicio.registrar_libro(
                    isbn, titulo, autor, editorial
                )

                mensaje = "El libro fue registrado correctamente."

            else:
                self._servicio.modificar_libro(
                    self._editando_id,
                    self._isbn_edicion,
                    titulo,
                    autor,
                    editorial
                )

                mensaje = "Los datos del libro fueron actualizados."

        except ValueError as error:
            self._mensaje("Datos inválidos", str(error))
            return

        self._editando_id = None
        self._modo = "consultar"
        self._dibujar()
        self._page.update()

        self._mensaje("Operación realizada", mensaje)

    def _editar_libro(self, datos):
        self._editando_id = datos[0]
        self._isbn_edicion = datos[1]

        self._isbn.value = datos[1]
        self._isbn.read_only = True
        self._titulo.value = datos[2]
        self._autor.value = datos[3]
        self._editorial.value = datos[4]

        self._titulo_formulario.value = "Modificar libro"
        self._boton_guardar.content = "Guardar cambios"
        self._boton_cancelar.visible = True
        self._cambiar_modo("registrar")

        self._page.update()

    def _ver_libro(self, datos):
        texto = (
            f"ISBN: {datos[1]}\n"
            f"Título: {datos[2]}\n"
            f"Autor: {datos[3]}\n"
            f"Editorial: {datos[4]}\n"
            f"Ejemplares totales: {datos[5]}\n"
            f"Ejemplares disponibles: {datos[6]}"
        )

        self._mensaje("Datos del libro", texto)

    def _vista_ejemplares(self):
        libros = self._servicio.listar_libros()
        sedes = self._servicio.listar_sedes_activas()

        self._codigo = ft.TextField(
            label="Código único del ejemplar"
        )

        self._libro = ft.Dropdown(
            label="Libro",
            width=260,
            options=[
                ft.DropdownOption(
                    key=str(l[0]),
                    text=f"{l[2]} - {l[1]}"
                )
                for l in libros
            ]
        )

        self._sede = ft.Dropdown(
            label="Sede",
            width=260,
            options=[
                ft.DropdownOption(
                    key=str(s[0]),
                    text=s[1]
                )
                for s in sedes
            ]
        )

        formulario = ft.Container(
            width=300,
            bgcolor="white",
            padding=20,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Nuevo ejemplar",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    ft.Text(
                        "Cada copia física tiene su propio código y sede.",
                        color="#678197",
                        size=12
                    ),
                    self._codigo,
                    self._libro,
                    self._sede,
                    ft.Button(
                        "Guardar ejemplar",
                        on_click=self._guardar_ejemplar,
                        bgcolor=self._celeste,
                        color=self._azul,
                        disabled=len(libros) == 0 or len(sedes) == 0
                    )
                ],
                spacing=14
            )
        )

        tarjetas = []
        for datos in self._servicio.listar_ejemplares():

            def ver(e, ejemplar=datos):
                self._ver_ejemplar(ejemplar)

            tarjetas.append(
                ft.Container(
                    bgcolor="#F1F7FC", padding=14, border_radius=11,
                    content=ft.Column([
                        ft.Text(
                            datos[2], size=14,
                            weight=ft.FontWeight.BOLD, color=self._azul
                        ),
                        ft.Text(datos[5], size=12, color="#59758B"),
                        ft.Text(
                            f"Código: {datos[1]}  ·  Propietaria: {datos[4]}",
                            size=12, color="#59758B"
                        ),
                        ft.Text(
                            f"Ubicación actual: {datos[8]}",
                            size=12, color="#59758B"
                        ),
                        ft.Row([
                            icono_accion("ver", "Ver detalles del ejemplar", ver)
                        ], spacing=6)
                    ], spacing=5)
                )
            )

        tarjetas_listado = ft.Column(
            controls=tarjetas or [
                ft.Text("Todavía no hay ejemplares registrados.",
                        color="#678197")
            ],
            spacing=10
        )

        listado = ft.Container(
            bgcolor="white",
            border_radius=12,
            padding=18,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Ejemplares registrados",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self._azul
                    ),
                    tarjetas_listado
                ],
                spacing=14
            )
        )

        return ft.Row(
            controls=[formulario, listado],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def _guardar_ejemplar(self, e):
        if not self._libro.value or not self._sede.value:
            self._mensaje(
                "Datos incompletos",
                "Seleccioná un libro y una sede."
            )
            return

        try:
            self._servicio.registrar_ejemplar(
                self._codigo.value or "",
                int(self._libro.value),
                int(self._sede.value)
            )

        except ValueError as error:
            self._mensaje("Datos inválidos", str(error))
            return

        self._modo = "consultar"
        self._dibujar()
        self._page.update()

        self._mensaje(
            "Operación realizada",
            "Ejemplar registrado correctamente."
        )

    def _ver_ejemplar(self, datos):
        texto = (
            f"Código: {datos[1]}\n"
            f"Libro: {datos[2]}\n"
            f"ISBN: {datos[3]}\n"
            f"Sede propietaria: {datos[4]}\n"
            f"Ubicación actual: {datos[8]}\n"
            f"Estado: {datos[5]}"
        )

        self._mensaje("Datos del ejemplar", texto)
