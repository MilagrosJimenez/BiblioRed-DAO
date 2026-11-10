
from datetime import date

from clases.tipos import EstadoReserva


class Reserva:

    def __init__(self, id_socio, id_libro, id_sede, *, id_reserva=None,
                 fecha=None, estado=EstadoReserva.PENDIENTE):

        if id_socio <= 0 or id_libro <= 0 or id_sede <= 0:
            raise ValueError(
                "Seleccioná un socio, un libro y una sede válidos"
            )

        self._id_socio = id_socio
        self._id_libro = id_libro
        self._id_sede = id_sede
        self._id_reserva = id_reserva
        self._fecha = fecha or date.today()
        self._estado = EstadoReserva(estado)

    def atender(self):
        self._resolver(EstadoReserva.ATENDIDA)

    def cancelar(self):
        self._resolver(EstadoReserva.CANCELADA)

    def _resolver(self, estado):
        if self._estado != EstadoReserva.PENDIENTE:
            raise ValueError("La reserva ya no está pendiente")
        self._estado = estado

    @property
    def id_reserva(self):
        return self._id_reserva

    @property
    def fecha(self):
        return self._fecha

    @property
    def id_sede_destino(self):
        return self._id_sede

    @property
    def id_socio(self):
        return self._id_socio

    @property
    def id_libro(self):
        return self._id_libro

    @property
    def id_sede(self):
        return self._id_sede

    @property
    def estado(self):
        return self._estado
