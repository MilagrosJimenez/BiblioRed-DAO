
from clases.prestamo import Prestamo

from datos.prestamos_efectivos_datos import (
    consultar_solicitudes_para_entrega,
    consultar_prestamos,
    registrar_prestamo
)


class PrestamosEfectivosServicio:

    def listar_solicitudes_listas(self):
        return consultar_solicitudes_para_entrega()

    def listar_prestamos(self):
        return consultar_prestamos()

    def registrar_entrega(self, id_solicitud, plazo_dias):
        prestamo = Prestamo(id_solicitud, plazo_dias)

        return registrar_prestamo(prestamo)
