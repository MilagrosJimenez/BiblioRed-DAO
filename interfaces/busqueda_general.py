"""Búsqueda por secciones del menú principal de BiblioRed.

No busca socios, sedes ni otros registros: permite encontrar rápidamente
las mismas opciones que aparecen en la barra de navegación lateral.
"""
from interfaces.ui_moderno import normalizar


def buscar_secciones(texto, secciones, limite=6):
    """Devuelve los nombres de menú que contienen el texto escrito."""
    termino = normalizar(texto)
    if not termino:
        return []
    return [
        nombre for nombre in secciones
        if termino in normalizar(nombre)
    ][:max(0, limite)]
