"""Búsqueda general de BiblioRed: únicamente consultas de lectura.

Busca simultáneamente sedes, socios, libros, ejemplares, solicitudes y
remitos. No modifica la base y permite buscar por fragmentos o números.
"""
from datos.base_datos import consultar_sedes, consultar_socios
from datos.catalogo_datos import consultar_libros, consultar_ejemplares
from datos.prestamos_datos import consultar_solicitudes
from datos.remitos_datos import consultar_remitos
from interfaces.ui_moderno import normalizar


def buscar_en_bibliored(texto, limite=6):
    termino = normalizar(texto)
    if not termino:
        return []

    opciones = []

    def incluir(tipo, titulo, detalle, destino):
        valor = normalizar(f"{tipo} {titulo} {detalle}")
        if termino in valor:
            opciones.append({
                "tipo": tipo,
                "titulo": titulo,
                "detalle": detalle,
                "destino": destino,
            })

    for s in consultar_sedes():
        incluir(
            "Sede", s[1],
            f"ID {s[0]} · {s[2]} · {'Activa' if s[5] else 'Dada de baja'}",
            "Administrar sedes",
        )

    for s in consultar_socios():
        incluir(
            "Socio", f"{s[3]}, {s[2]}",
            f"Documento {s[1]} · {'Habilitado' if s[6] else 'Inhabilitado'}",
            "Administrar socios",
        )

    for l in consultar_libros():
        incluir("Libro", l[2], f"ISBN {l[1]} · {l[3]}", "Catálogo y ejemplares")

    for e in consultar_ejemplares():
        incluir(
            "Ejemplar", e[1],
            f"{e[2]} · Sede {e[4]} · {e[5]}",
            "Catálogo y ejemplares",
        )

    for s in consultar_solicitudes():
        incluir(
            "Solicitud", f"N.º {s[0]} · {s[1]}",
            f"{s[3]} · {s[5]} → {s[6]} · {s[8]}",
            "Solicitudes de préstamo",
        )

    for r in consultar_remitos():
        incluir(
            "Remito", f"N.º {r[0]} · {r[1]}",
            f"{r[3]} → {r[4]} · {r[5]}",
            "Remitos y traslados",
        )

    return opciones[:max(0, limite)]
