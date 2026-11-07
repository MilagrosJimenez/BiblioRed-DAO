"""Casos de uso de inventario, historial y reportes."""
from datos.consultas_bibliored_datos import (
    consultar_inventario, consultar_historial_lecturas, REPORTES
)


class ConsultasBiblioredServicio:
    def inventario(self, codigo="", sede=None):
        return consultar_inventario(codigo, sede)

    def historial(self, id_socio):
        return consultar_historial_lecturas(id_socio)

    def reporte(self, clave):
        if clave not in REPORTES:
            raise ValueError("Reporte desconocido")
        titulo, columnas, consulta = REPORTES[clave]
        return titulo, columnas, consulta()
