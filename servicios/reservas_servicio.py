
from clases.reserva import Reserva

from datos.base_datos import consultar_sedes, consultar_socios
from datos.catalogo_datos import consultar_libros

from datos.reservas_datos import (
    consultar_disponibilidad,
    consultar_reservas,
    guardar_reserva,
    atender_reserva,
    cancelar_reserva
)


class ReservasServicio:

    def listar_socios_habilitados(self):
        return [
            s for s in consultar_socios()
            if s[6] == 1
        ]

    def listar_sedes_activas(self):
        return [
            s for s in consultar_sedes()
            if s[5] == 1
        ]

    def listar_libros(self):
        return consultar_libros()

    def listar_disponibilidad(self):
        return consultar_disponibilidad()

    def listar_reservas(self):
        return consultar_reservas()

    def registrar(self, id_socio, id_libro, id_sede):
        reserva = Reserva(id_socio, id_libro, id_sede)
        return guardar_reserva(reserva)

    def atender(self, id_reserva):
        return atender_reserva(id_reserva)

    def cancelar(self, id_reserva):
        cancelar_reserva(id_reserva)
