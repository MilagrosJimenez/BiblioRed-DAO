
from datetime import date
from clases.tipos import EstadoFisico


class Devolucion:
    def __init__(self, id_prestamo: int, estado_fisico: str,
                 observaciones: str = "", *, id_devolucion=None) -> None:

        if id_prestamo <= 0:
            raise ValueError("Debe seleccionar un préstamo válido")

        if estado_fisico not in ("Bueno", "Dañado"):
            raise ValueError("Seleccioná el estado físico del ejemplar")

        self._id_prestamo = id_prestamo
        self._id_devolucion = id_devolucion
        self._estado_fisico = EstadoFisico(estado_fisico)
        self._observaciones = observaciones.strip()
        self._fecha = date.today()

    @property
    def id_devolucion(self):
        return self._id_devolucion

    @property
    def id_prestamo(self):
        return self._id_prestamo

    @property
    def estado_fisico(self):
        return self._estado_fisico

    @property
    def observaciones(self):
        return self._observaciones

    @property
    def fecha(self):
        return self._fecha
