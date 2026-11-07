"""Generación de los cuatro reportes no triviales en PDF con ReportLab."""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
)

from servicios.consultas_bibliored_servicio import ConsultasBiblioredServicio


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
    elementos.append(tabla)
    documento.build(elementos)
    return archivo
