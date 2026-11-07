"""Diseño visual compartido y búsquedas instantáneas de BiblioRed.

No ejecuta consultas ni altera datos: solamente presenta y filtra controles
ya cargados. Compatible con Flet 1.0.5.
"""
import unicodedata
import flet as ft


TINTA = "#142B49"
AZUL = "#2563EB"
AZUL_OSCURO = "#123353"
APAGADO = "#667B93"
FONDO = "#F3F7FC"
BORDE = "#E2EAF3"
CLARO = "#F7FAFE"
CELESTE = "#DCEFFC"


def normalizar(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    return "".join(
        letra for letra in texto if not unicodedata.combining(letra)
    ).casefold().strip()


def texto_visible(control):
    """Obtiene texto visible de celdas, etiquetas y tarjetas."""
    if control is None:
        return ""
    if isinstance(control, ft.Text):
        return str(control.value or "")
    partes = []
    for atributo in ("content", "title", "subtitle"):
        hijo = getattr(control, atributo, None)
        if hijo is not None:
            partes.append(texto_visible(hijo))
    for atributo in ("controls", "cells"):
        hijos = getattr(control, atributo, None)
        if isinstance(hijos, (list, tuple)):
            partes.extend(texto_visible(hijo) for hijo in hijos)
    return " ".join(partes)


def buscador_de_tabla(tabla, page):
    """Filtra sin recargar datos. Funciona con letras, dígitos, tildes y Enter."""
    originales = list(tabla.rows)
    cantidad = ft.Text(
        f"{len(originales)} registros",
        size=11,
        color=APAGADO,
    )
    campo = ft.TextField(
        label="Buscar en esta lista",
        hint_text="Escribí un nombre, DNI, código, número...",
        width=330,
        border_radius=10,
        border_color=BORDE,
        focused_border_color=AZUL,
        text_size=13,
    )

    def filtrar(e=None):
        termino = normalizar(campo.value)
        tabla.rows = [
            fila for fila in originales
            if not termino or termino in normalizar(texto_visible(fila))
        ]
        cantidad.value = f"{len(tabla.rows)} de {len(originales)} registros"
        page.update()

    campo.on_change = filtrar
    campo.on_submit = filtrar
    return ft.Row([campo, cantidad], spacing=12, wrap=True)


def buscador_de_tarjetas(columna, page):
    originales = list(columna.controls)
    cantidad = ft.Text(f"{len(originales)} elementos", size=11, color=APAGADO)
    campo = ft.TextField(
        label="Buscar en esta lista",
        hint_text="Filtrar por nombre, número, libro o estado...",
        width=330,
        border_radius=10,
        border_color=BORDE,
        focused_border_color=AZUL,
        text_size=13,
    )

    def filtrar(e=None):
        termino = normalizar(campo.value)
        visibles = [
            control for control in originales
            if not termino or termino in normalizar(texto_visible(control))
        ]
        columna.controls = visibles or [
            ft.Text("No hay resultados para esta búsqueda.", color=APAGADO)
        ]
        cantidad.value = f"{len(visibles)} de {len(originales)} elementos"
        page.update()

    campo.on_change = filtrar
    campo.on_submit = filtrar
    return ft.Row([campo, cantidad], spacing=12, wrap=True)


def personalizar_controles(control):
    """Una estética única para formularios y listados antiguos y nuevos."""
    if control is None:
        return
    if isinstance(control, ft.Container):
        color = normalizar(getattr(control, "bgcolor", None))
        if color in ("white", "#ffffff"):
            control.bgcolor = "#FFFFFF"
            control.border_radius = 15
            control.border = ft.Border.all(1, BORDE)
        elif color in ("#f1f7fc", "#e4f2fc"):
            control.bgcolor = CLARO
            control.border_radius = 11
            control.border = ft.Border.all(1, BORDE)
    elif isinstance(control, ft.TextField):
        control.border_radius = 10
        control.border_color = BORDE
        control.focused_border_color = AZUL
        control.cursor_color = AZUL
        control.text_size = 13
    elif isinstance(control, ft.Dropdown):
        control.border_radius = 10
        control.border_color = BORDE
        control.focused_border_color = AZUL
        control.text_size = 13
    elif isinstance(control, ft.DataTable):
        control.heading_row_color = "#EDF4FC"
        control.column_spacing = 18
        control.divider_thickness = 0.7
    elif isinstance(control, ft.Button):
        control.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=9),
            elevation=0,
        )
        control.height = 40
        # Se respeta disabled y on_click originales.
        if normalizar(control.bgcolor) in ("#63bdeb", "#bce7ff"):
            control.bgcolor = AZUL
            control.color = "#FFFFFF"

    if isinstance(control, (ft.Row, ft.Column)):
        for hijo in list(control.controls):
            personalizar_controles(hijo)
    elif isinstance(control, ft.Container):
        personalizar_controles(control.content)


def instalar_busquedas(control, page):
    """Busca tablas y colecciones de tarjetas sin tocar su lógica interna."""
    if control is None:
        return
    if isinstance(control, ft.Column):
        # Listados de tablas: título + Row(scroll, DataTable).
        for indice, hijo in enumerate(list(control.controls)):
            if isinstance(hijo, ft.Row):
                tablas = [c for c in hijo.controls if isinstance(c, ft.DataTable)]
                if tablas:
                    ya_instalado = any(
                        isinstance(x, ft.Row) and any(
                            isinstance(y, ft.TextField)
                            and y.label == "Buscar en esta lista"
                            for y in x.controls
                        ) for x in control.controls
                    )
                    if not ya_instalado:
                        control.controls.insert(
                            indice, buscador_de_tabla(tablas[0], page)
                        )
                    break

        # Listados de tarjetas: título + Column de registros.
        titulos = [
            normalizar(c.value) for c in control.controls
            if isinstance(c, ft.Text)
        ]
        es_listado = any(
            any(p in titulo for p in (
                "registrad", "catalogo", "remitos", "prestamos", "devoluciones",
                "reservas", "historial de movimientos"
            )) for titulo in titulos
        )
        if es_listado:
            for indice, hijo in enumerate(list(control.controls)):
                if isinstance(hijo, ft.Column) and any(
                    isinstance(x, ft.Container) for x in hijo.controls
                ):
                    ya_instalado = any(
                        isinstance(x, ft.Row) and any(
                            isinstance(y, ft.TextField)
                            and y.label == "Buscar en esta lista"
                            for y in x.controls
                        ) for x in control.controls
                    )
                    if not ya_instalado:
                        control.controls.insert(
                            indice, buscador_de_tarjetas(hijo, page)
                        )
                    break

    if isinstance(control, (ft.Column, ft.Row)):
        for hijo in list(control.controls):
            instalar_busquedas(hijo, page)
    elif isinstance(control, ft.Container):
        instalar_busquedas(control.content, page)


def modernizar(control, page):
    personalizar_controles(control)
    instalar_busquedas(control, page)
