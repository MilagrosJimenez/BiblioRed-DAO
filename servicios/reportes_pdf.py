"""Generación de los cuatro reportes no triviales en PDF con ReportLab."""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
)

from servicios.consultas_bibliored_servicio import ConsultasBiblioredServicio



def crear_grafico(clave, encabezados, filas):
    """Gráfico horizontal con las primeras ocho filas del reporte."""
    if not filas:
        return None
    series = {
        "prestamos": (1, 2),
        "solicitados": (2,),
        "disponibilidad": (2, 3),
        "movimientos": (2, 3),
    }[clave]
    colores = [colors.HexColor("#2377B9"), colors.HexColor("#E58D37")]
    datos = []
    for fila in filas[:8]:
        etiqueta = " / ".join(str(fila[i]) for i in ((0, 1) if clave == "movimientos" else (0,)))
        if clave == "disponibilidad":
            etiqueta = str(fila[0]) + " / " + str(fila[1])
        numeros = [max(0, float(fila[i] or 0)) for i in series]
        datos.append((etiqueta[:35], numeros))
    maximo = max((max(numeros) for _, numeros in datos), default=0) or 1
    ancho, alto_fila = 755, 42 if len(series) > 1 else 31
    alto = len(datos) * alto_fila + 55
    dibujo = Drawing(ancho, alto)
    dibujo.add(String(4, alto - 13, "Resumen gráfico (hasta 8 categorías)", fontSize=11,
                      fillColor=colors.HexColor("#153D63")))
    for i, columna in enumerate(series):
        dibujo.add(Rect(230 + i * 175, alto - 35, 10, 10, fillColor=colores[i],
                         strokeColor=None))
        dibujo.add(String(244 + i * 175, alto - 33, str(encabezados[columna]),
                           fontSize=9))
    max_ancho = 440
    for i, (etiqueta, numeros) in enumerate(datos):
        y = alto - 62 - i * alto_fila
        dibujo.add(String(4, y + 3, etiqueta, fontSize=8))
        for j, numero in enumerate(numeros):
            bajo = y - j * 15
            largo = (numero / maximo) * max_ancho
            dibujo.add(Rect(245, bajo, largo, 12, fillColor=colores[j], strokeColor=None))
            dibujo.add(String(min(695, 250 + largo), bajo + 2, f"{numero:g}",
                              fontSize=8))
        dibujo.add(Line(240, y - 17 if len(series) > 1 else y - 4, 750,
                         y - 17 if len(series) > 1 else y - 4,
                         strokeColor=colors.HexColor("#E9EDF2"), strokeWidth=0.4))
    return dibujo


def generar_reporte(clave):
    titulo, encabezados, filas = ConsultasBiblioredServicio().reporte(clave)

    destino = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "reportes_generados"
    ))
    os.makedirs(destino, exist_ok=True)
    archivo = os.path.join(destino, f"{clave}_{datetime.now():%Y%m%d_%H%M%S}.pdf")

    estilos = getSampleStyleSheet()
    documento = SimpleDocTemplate(
        archivo, pagesize=landscape(A4),
        leftMargin=1.3 * cm, rightMargin=1.3 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm
    )
    elementos = [
        Paragraph("BiblioRed | UTN FRC - Grupo 73", estilos["Heading2"]),
        Paragraph(titulo, estilos["Title"]),
        Paragraph(
            f"Generado el {datetime.now():%d/%m/%Y %H:%M} | "
            f"Registros: {len(filas)}", estilos["Normal"]
        ),
        Spacer(1, 0.5 * cm)
    ]

    estilo_celda = estilos["BodyText"]
    estilo_celda.fontSize = 8
    estilo_celda.leading = 10

    def celda(valor):
        if valor is None:
            valor = "Sin recepciones"
        import html
        return Paragraph(html.escape(str(valor)), estilo_celda)

    tabla_datos = [[celda(col) for col in encabezados]]
    tabla_datos += [[celda(v) for v in fila] for fila in filas]
    if not filas:
        tabla_datos.append([celda("Sin registros")] + [celda("")] * (len(encabezados)-1))

    ancho = landscape(A4)[0] - 2.6 * cm
    tabla = LongTable(
        tabla_datos, colWidths=[ancho / len(encabezados)] * len(encabezados),
        repeatRows=1, hAlign="LEFT"
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D8ECFA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F7FC")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#16436D")),
    ]))
    grafico = crear_grafico(clave, encabezados, filas)
    if grafico is not None:
        elementos.append(grafico)
        elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(tabla)
    documento.build(elementos)
    return archivo
