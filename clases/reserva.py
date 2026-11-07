
class Reserva:

    def __init__(self, id_socio, id_libro, id_sede):

        if id_socio <= 0 or id_libro <= 0 or id_sede <= 0:
            raise ValueError(
                "Seleccioná un socio, un libro y una sede válidos"
            )

        self._id_socio = id_socio
        self._id_libro = id_libro
        self._id_sede = id_sede
        self._estado = "Pendiente"

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