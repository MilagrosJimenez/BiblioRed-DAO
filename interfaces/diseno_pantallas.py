"""Composición visual compacta de los módulos iniciales de BiblioRed.

Solo organiza controles Flet existentes. Conserva sus callbacks y no
accede a SQLite. En formularios y consultas usa un mismo ancho de trabajo.
"""
import flet as ft
from interfaces.ui_moderno import buscador_de_tarjetas, sugerencia_de_busqueda

ANCHO = 944
ANCHO_INTERIOR = 890
AZUL = "#173758"
BORDE = "#E0E8F2"


def centrar(control):
    return ft.Row(
        controls=[control],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
    )


def _organizar_panel(formulario, contenido):
    formulario.width = ANCHO
    formulario.height = None
    formulario.expand = False
    formulario.padding = 20
    formulario.bgcolor = "#FFFFFF"
    formulario.border_radius = 14
    formulario.content = ft.Column(
        controls=contenido,
        spacing=12,
    )


def preparar_formulario_sedes(formulario, ventana):
    v = ventana
    v._campo_id.width = 165
    v._campo_nombre.width = 380
    v._campo_telefono.width = 270
    v._campo_direccion.width = 839
    for selector in (v._dia_desde, v._dia_hasta,
                     v._hora_desde, v._hora_hasta):
        selector.width = 197

    dias = ft.Column([
        ft.Text("Días de atención", weight=ft.FontWeight.BOLD,
                color=AZUL, size=13),
        ft.Row([v._dia_desde, v._dia_hasta], spacing=10),
    ], spacing=7)
    horas = ft.Column([
        ft.Row([
            ft.Text("Horario de atención", weight=ft.FontWeight.BOLD,
                    color=AZUL, size=13),
            v._atencion_24h,
        ], spacing=8),
        ft.Row([v._hora_desde, v._hora_hasta], spacing=10),
    ], spacing=7)
    _organizar_panel(formulario, [
        v._titulo_formulario,
        ft.Row([v._campo_id, v._campo_nombre, v._campo_telefono],
               spacing=12),
        v._campo_direccion,
        ft.Row([dias, horas], spacing=22),
        v._horario_actual,
        v._vista_previa,
        ft.Row([v._boton_guardar, v._boton_cancelar], spacing=12)
    ])


def preparar_formulario_socios(formulario, pantalla):
    p = pantalla
    for campo in (
        p._campo_documento, p._campo_telefono,
        p._campo_nombre, p._campo_apellido,
    ):
        campo.width = 414
    p._campo_correo.width = 840
    _organizar_panel(formulario, [
        p._titulo_formulario,
        ft.Row([p._campo_documento, p._campo_telefono], spacing=12),
        ft.Row([p._campo_nombre, p._campo_apellido], spacing=12),
        p._campo_correo,
        ft.Row([p._boton_guardar, p._boton_cancelar], spacing=12)
    ])


def preparar_formulario_solicitudes(formulario, pantalla):
    p = pantalla
    p._socio.width = 410
    p._ejemplar.width = 410
    p._destino.width = 836
    controles = formulario.content.controls
    # Preservamos todas las ayudas y el botón original.
    titulo, ayuda, _, _, _, explicacion, boton = controles
    _organizar_panel(formulario, [
        titulo, ayuda,
        ft.Row([p._socio, p._ejemplar], spacing=16),
        p._destino,
        explicacion,
        boton,
    ])


def preparar_formulario_remitos(formulario, pantalla):
    controles = formulario.content.controls
    titulo, ayuda, selector, boton, nota = controles
    selector.width = 830
    _organizar_panel(formulario, [
        titulo, ayuda, selector, boton, nota,
    ])


def preparar_formulario_catalogo(formulario, pantalla):
    if pantalla._seccion == "libros":
        for campo in (
            pantalla._isbn, pantalla._titulo,
            pantalla._autor, pantalla._editorial,
        ):
            campo.width = 412
        _organizar_panel(formulario, [
            pantalla._titulo_formulario,
            ft.Row([pantalla._isbn, pantalla._titulo], spacing=14),
            ft.Row([pantalla._autor, pantalla._editorial], spacing=14),
            ft.Row([pantalla._boton_guardar, pantalla._boton_cancelar],
                   spacing=12),
        ])
    else:
        titulo, ayuda, _, _, _, boton = formulario.content.controls
        pantalla._codigo.width = 410
        pantalla._libro.width = 410
        pantalla._sede.width = 830
        _organizar_panel(formulario, [
            titulo, ayuda,
            ft.Row([pantalla._codigo, pantalla._libro], spacing=14),
            pantalla._sede,
            boton,
        ])


def _fila_distribuida(celdas, pesos, encabezado=False):
    columnas = []
    for celda, peso in zip(celdas, pesos):
        control = celda if encabezado else celda.content
        if isinstance(control, ft.Text):
            control.size = 12 if encabezado else 13
            if encabezado:
                control.weight = ft.FontWeight.BOLD
        columnas.append(ft.Container(content=control, expand=peso))
    return ft.Container(
        bgcolor="#E9F1FC" if encabezado else "#FFFFFF",
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDE)),
        content=ft.Row(columnas, spacing=10, wrap=False),
    )


def tabla_como_listado(tabla, pesos, vacio="No hay registros todavía."):
    """Filas completas y buscables en toda la anchura disponible.

    Se reutilizan las DataCell existentes, incluyendo los callbacks de
    Ver/Editar/Habilitar, para no alterar reglas ni operaciones.
    """
    registros = [
        _fila_distribuida(fila.cells, pesos)
        for fila in tabla.rows
    ]
    return ft.Column(
        controls=[
            _fila_distribuida([col.label for col in tabla.columns],
                             pesos, encabezado=True),
            *registros,
        ] if registros else [
            ft.Text(vacio, color="#60768D", size=13)
        ],
        spacing=0,
    )


def preparar_listado_tabla(listado, pesos, page):
    controles = listado.content.controls
    titulo = controles[0]
    tabla = next(
        c for nodo in controles if isinstance(nodo, ft.Row)
        for c in nodo.controls if isinstance(c, ft.DataTable)
    )
    listado.width = ANCHO
    listado.expand = False
    listado.padding = 20
    tabla_visual = tabla_como_listado(tabla, pesos)
    encabezado = tabla_visual.controls[0] if tabla.rows else None
    registros = ft.Column(
        controls=tabla_visual.controls[1:] if tabla.rows else [],
        spacing=0
    )
    contenido = [
        titulo,
        buscador_de_tarjetas(
            registros, page, sugerencia_de_busqueda([titulo.value])
        )
    ]
    if encabezado is not None:
        contenido.append(encabezado)
    else:
        contenido.append(
            ft.Text("Todavía no hay registros.", color="#60768D", size=13)
        )
    contenido.append(registros)
    listado.content = ft.Column(
        controls=contenido,
        spacing=13,
    )


def preparar_listado_tarjetas(listado):
    listado.width = ANCHO
    listado.expand = False
    listado.padding = 20
    if not isinstance(listado.content, ft.Column):
        return
    for elemento in listado.content.controls:
        if isinstance(elemento, ft.Column):
            elemento.scroll = None
            for tarjeta in elemento.controls:
                if isinstance(tarjeta, ft.Container):
                    tarjeta.width = ANCHO_INTERIOR


def preparar_pantalla_segunda_etapa(vista, pantalla, page, tipo,
                                   registrar, consultar):
    """Separa alta y consulta en los módulos restantes.

    Conserva campos, validaciones y callbacks originales; modifica
    únicamente su presentación. No vuelve a consultar la base de datos.
    """
    formulario, listado = vista.controls
    controles = formulario.content.controls
    if tipo == "prestamos":
        titulo, ayuda, _, _, explicacion, boton = controles
        pantalla._solicitud.width = 590
        pantalla._plazo.width = 238
        nuevos = [
            titulo, ayuda,
            ft.Row([pantalla._solicitud, pantalla._plazo], spacing=14),
            explicacion, boton,
        ]
    elif tipo == "devoluciones":
        titulo, ayuda, _, _, _, boton, explicacion = controles
        pantalla._prestamo.width = 565
        pantalla._estado_fisico.width = 263
        pantalla._observaciones.width = 842
        nuevos = [
            titulo, ayuda,
            ft.Row([pantalla._prestamo, pantalla._estado_fisico], spacing=14),
            pantalla._observaciones, boton, explicacion,
        ]
    elif tipo == "retornos":
        titulo, ayuda, selector, boton, nota = controles
        selector.width = 842
        nuevos = [titulo, ayuda, selector, boton, nota]
    elif tipo == "reservas":
        titulo, ayuda, _, _, _, boton = controles
        pantalla._socio.width = 414
        pantalla._libro.width = 414
        pantalla._sede.width = 842
        nuevos = [
            titulo, ayuda,
            ft.Row([pantalla._socio, pantalla._libro], spacing=14),
            pantalla._sede, boton,
        ]
    else:
        raise ValueError("Formulario desconocido: " + tipo)

    _organizar_panel(formulario, nuevos)
    preparar_listado_tarjetas(listado)
    registros = next(
        (c for c in listado.content.controls if isinstance(c, ft.Column)),
        None
    )
    if registros is not None and any(
        isinstance(c, ft.Container) for c in registros.controls
    ):
        titulo_lista = listado.content.controls[0]
        listado.content.controls.insert(
            1, buscador_de_tarjetas(
                registros, page, sugerencia_de_busqueda([titulo_lista.value])
            )
        )

    boton_registrar = ft.Button(registrar)
    boton_consultar = ft.Button(consultar)
    zona = ft.Column(spacing=0)

    def seleccionar(modo, actualizar=True):
        pantalla._modo = modo
        for boton, activo in (
            (boton_registrar, modo == "registrar"),
            (boton_consultar, modo == "consultar"),
        ):
            boton.bgcolor = "#2563EB" if activo else "#FFFFFF"
            boton.color = "#FFFFFF" if activo else "#142B49"
        zona.controls = [
            centrar(formulario if modo == "registrar" else listado)
        ]
        if actualizar:
            page.update()

    boton_registrar.on_click = lambda e: seleccionar("registrar")
    boton_consultar.on_click = lambda e: seleccionar("consultar")
    seleccionar(getattr(pantalla, "_modo", "consultar"), actualizar=False)
    return ft.Column([
        ft.Row([boton_registrar, boton_consultar], spacing=12),
        zona,
    ], spacing=13)
