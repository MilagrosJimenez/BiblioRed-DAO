"""Informes PDF de BiblioRed: tablas legibles y gráficos basados en datos reales."""
import os
from datetime import datetime

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from servicios.consultas_bibliored_servicio import ConsultasBiblioredServicio

AZUL = colors.HexColor("#153D63")
TURQUESA = colors.HexColor("#167DA7")
NARANJA = colors.HexColor("#E99746")
TEXTO = colors.HexColor("#23364B")
GRIS = colors.HexColor("#687B8D")
FONDO = colors.HexColor("#F0F5FA")
LINEA = colors.HexColor("#DCE5EE")
BLANCO = colors.white
ANCHO_PAGINA, ALTO_PAGINA = landscape(A4)
MARGEN = 1.25 * cm
ANCHO_CONTENIDO = ANCHO_PAGINA - 2 * MARGEN

ESTILOS = {
    "marca": ParagraphStyle("MarcaBiblioRed", fontName="Helvetica-Bold", fontSize=10,
                              leading=13, textColor=AZUL),
    "titulo": ParagraphStyle("TituloBiblioRed", fontName="Helvetica-Bold", fontSize=20,
                               leading=24, textColor=AZUL, spaceAfter=3),
    "subtitulo": ParagraphStyle("SubtituloBiblioRed", fontName="Helvetica", fontSize=9,
                                  leading=12, textColor=GRIS),
    "seccion": ParagraphStyle("SeccionBiblioRed", fontName="Helvetica-Bold", fontSize=10,
                                leading=13, textColor=AZUL, spaceAfter=7),
    "etiqueta": ParagraphStyle("EtiquetaBiblioRed", fontName="Helvetica", fontSize=8,
                                 leading=10, textColor=GRIS),
    "numero": ParagraphStyle("NumeroBiblioRed", fontName="Helvetica-Bold", fontSize=18,
                               leading=21, textColor=AZUL),
    "celda": ParagraphStyle("CeldaBiblioRed", fontName="Helvetica", fontSize=8.4,
                              leading=11, textColor=TEXTO, wordWrap="CJK"),
    "cabecera": ParagraphStyle("CabeceraBiblioRed", fontName="Helvetica-Bold", fontSize=8.3,
                                 leading=11, textColor=BLANCO),
    "aviso": ParagraphStyle("AvisoBiblioRed", fontName="Helvetica", fontSize=9,
                              leading=13, textColor=AZUL),
}


def _texto(valor):
    from xml.sax.saxutils import escape
    return escape("" if valor is None else str(valor))


def _resumen(clave, filas):
    if clave == "prestamos":
        return (("Sedes incluidas", len(filas)),
                ("Préstamos activos", sum(int(f[1] or 0) for f in filas)),
                ("Préstamos vencidos", sum(int(f[2] or 0) for f in filas)))
    if clave == "solicitados":
        return (("Títulos solicitados", len(filas)),
                ("Solicitudes registradas", sum(int(f[2] or 0) for f in filas)),
                ("Más solicitado", max((int(f[2] or 0) for f in filas), default=0)))
    if clave == "disponibilidad":
        return (("Sede / título", len(filas)),
                ("Ejemplares", sum(int(f[2] or 0) for f in filas)),
                ("Ejemplares libres", sum(int(f[3] or 0) for f in filas)))
    if clave == "movimientos":
        return (("Rutas de traslado", len(filas)),
                ("Envíos registrados", sum(int(f[2] or 0) for f in filas)),
                ("Envíos recibidos", sum(int(f[3] or 0) for f in filas)))
    raise ValueError("Reporte desconocido")


def _datos_grafico(clave, filas):
    resultado = []
    for f in filas:
        if clave == "prestamos":
            total = max(0, int(f[1] or 0))
            segundo = min(total, max(0, int(f[2] or 0)))
            valores = (total - segundo, segundo)
            nombre = str(f[0])
            leyenda = ("En plazo", "Vencidos")
        elif clave == "solicitados":
            total = max(0, int(f[2] or 0))
            valores = (total, 0)
            nombre = str(f[0])
            leyenda = ("Solicitudes", "")
        elif clave == "disponibilidad":
            total = max(0, int(f[2] or 0))
            libre = min(total, max(0, int(f[3] or 0)))
            valores = (libre, total - libre)
            nombre = str(f[0]) + " / " + str(f[1])
            leyenda = ("Libres", "No libres")
        elif clave == "movimientos":
            total = max(0, int(f[2] or 0))
            recibidos = min(total, max(0, int(f[3] or 0)))
            valores = (recibidos, total - recibidos)
            nombre = str(f[0]) + " / " + str(f[1])
            leyenda = ("Recibidos", "Sin recibir")
        else:
            raise ValueError("Reporte desconocido")
        resultado.append((nombre, valores, total))
    return leyenda, resultado


def crear_grafico(clave, encabezados, filas):
    """Gráfico de hasta cinco categorías; no dibujar barras sin valores."""
    if not filas:
        return None
    leyenda, datos = _datos_grafico(clave, filas)
    datos = sorted(datos, key=lambda d: d[2], reverse=True)[:5]
    maximo = max((d[2] for d in datos), default=0)
    if maximo <= 0:
        return None
    ancho = ANCHO_CONTENIDO
    alto = 36 + len(datos) * 23
    dibujo = Drawing(ancho, alto)
    dibujo.add(String(0, alto - 12, "Distribución (5 categorías con mayor valor)",
                       fontName="Helvetica-Bold", fontSize=10, fillColor=AZUL))
    dibujo.add(Rect(0, alto - 30, 9, 9, fillColor=TURQUESA, strokeColor=None))
    dibujo.add(String(14, alto - 28, leyenda[0], fontSize=8, fillColor=TEXTO))
    if leyenda[1]:
        dibujo.add(Rect(105, alto - 30, 9, 9, fillColor=NARANJA, strokeColor=None))
        dibujo.add(String(119, alto - 28, leyenda[1], fontSize=8, fillColor=TEXTO))
    inicio = 240
    ancho_barra = ancho - inicio - 45
    for i, (nombre, valores, total) in enumerate(datos):
        y = alto - 49 - i * 23
        etiqueta = nombre if len(nombre) <= 39 else nombre[:36] + "..."
        dibujo.add(String(0, y + 4, etiqueta, fontSize=8, fillColor=TEXTO))
        dibujo.add(Rect(inicio, y, ancho_barra, 12, fillColor=FONDO, strokeColor=None))
        acum = inicio
        for valor, color in zip(valores, (TURQUESA, NARANJA)):
            segmento = valor / maximo * ancho_barra
            if segmento > 0:
                dibujo.add(Rect(acum, y, segmento, 12, fillColor=color, strokeColor=None))
                acum += segmento
        dibujo.add(String(inicio + ancho_barra + 7, y + 3, str(total),
                           fontName="Helvetica-Bold", fontSize=8, fillColor=AZUL))
    return dibujo


def _tarjetas(clave, filas):
    internos = []
    for etiqueta, valor in _resumen(clave, filas):
        t = Table([[Paragraph(_texto(etiqueta), ESTILOS["etiqueta"])],
                   [Paragraph(_texto(valor), ESTILOS["numero"])]],
                  colWidths=[ANCHO_CONTENIDO / 3 - 25])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        internos.append(t)
    tabla = Table([internos], colWidths=[ANCHO_CONTENIDO / 3] * 3, rowHeights=[55])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FONDO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBEFORE", (1, 0), (-1, -1), 1, BLANCO),
    ]))
    return tabla


def _anchos(clave):
    proporciones = {
        "prestamos": (0.42, 0.19, 0.19, 0.20),
        "solicitados": (0.54, 0.26, 0.20),
        "disponibilidad": (0.23, 0.38, 0.13, 0.13, 0.13),
        "movimientos": (0.27, 0.27, 0.15, 0.15, 0.16),
    }[clave]
    return [ANCHO_CONTENIDO * x for x in proporciones]


def _tabla(clave, encabezados, filas):
    tabla_datos = [[Paragraph(_texto(c), ESTILOS["cabecera"]) for c in encabezados]]
    for fila in filas:
        tabla_datos.append([Paragraph(_texto(v if v is not None else "—"),
                                       ESTILOS["celda"]) for v in fila])
    if not filas:
        tabla_datos.append([Paragraph("No hay registros para mostrar", ESTILOS["celda"])]
                            + [""] * (len(encabezados) - 1))
    tabla = Table(tabla_datos, colWidths=_anchos(clave), repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, FONDO]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, LINEA),
    ]))
    return tabla


def _pie(canvas, doc):
    canvas.setStrokeColor(LINEA)
    canvas.setLineWidth(0.6)
    canvas.line(MARGEN, 27, ANCHO_PAGINA - MARGEN, 27)
    canvas.setFillColor(GRIS)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGEN, 15, "BiblioRed | Desarrollo de Aplicaciones con Objetos | Grupo 73")
    canvas.drawRightString(ANCHO_PAGINA - MARGEN, 15, f"Página {doc.page}")


def construir_pdf(clave, titulo, encabezados, filas, archivo):
    """Diseño independiente de SQLite para verificar sin modificar datos."""
    documento = SimpleDocTemplate(
        str(archivo), pagesize=landscape(A4),
        leftMargin=MARGEN, rightMargin=MARGEN,
        topMargin=0.95 * cm, bottomMargin=1.25 * cm,
        title=f"BiblioRed - {titulo}", author="BiblioRed | UTN FRC - Grupo 73",
    )
    ahora = datetime.now()
    elementos = [
        Paragraph("BIBLIORED  /  UTN FRC  /  GRUPO 73", ESTILOS["marca"]),
        Spacer(1, 9),
        Paragraph(_texto(titulo), ESTILOS["titulo"]),
        Paragraph(f"Informe generado el {ahora:%d/%m/%Y a las %H:%M}  ·  "
                  f"{len(filas)} filas de resultados", ESTILOS["subtitulo"]),
        Spacer(1, 17),
        _tarjetas(clave, filas),
        Spacer(1, 14),
    ]
    grafico = crear_grafico(clave, encabezados, filas)
    if grafico is None:
        aviso = ("No hay valores positivos para graficar con los registros actuales. "
                 "El informe conserva el detalle real de la base de datos; "
                 "no se crean préstamos ni valores ficticios.")
        t = Table([[Paragraph(_texto(aviso), ESTILOS["aviso"])]],
                  colWidths=[ANCHO_CONTENIDO])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), FONDO),
            ("LEFTPADDING", (0, 0), (-1, -1), 13),
            ("RIGHTPADDING", (0, 0), (-1, -1), 13),
            ("TOPPADDING", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ]))
        elementos += [t, Spacer(1, 15)]
    else:
        elementos += [grafico, Spacer(1, 13)]
    elementos += [
        Paragraph("DETALLE DEL REPORTE", ESTILOS["seccion"]),
        _tabla(clave, encabezados, filas),
    ]
    documento.build(elementos, onFirstPage=_pie, onLaterPages=_pie)
    return str(archivo)


def generar_reporte(clave):
    titulo, encabezados, filas = ConsultasBiblioredServicio().reporte(clave)
    destino = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "reportes_generados"
    ))
    os.makedirs(destino, exist_ok=True)
    archivo = os.path.join(destino, f"{clave}_{datetime.now():%Y%m%d_%H%M%S}.pdf")
    return construir_pdf(clave, titulo, encabezados, filas, archivo)
