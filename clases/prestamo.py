from datetime import date
from clases.estrategia_plazo import seleccionar_estrategia


class Prestamo:
    """Préstamo que delega el vencimiento a una estrategia intercambiable."""

    def __init__(self, id_solicitud: int, plazo_dias: int) -> None:
        if id_solicitud <= 0:
            raise ValueError("Debe seleccionar una solicitud válida")

        self._id_solicitud = id_solicitud
        self._fecha_prestamo = date.today()
        self._estrategia_plazo = seleccionar_estrategia(plazo_dias)
        self._fecha_vencimiento = self.calcular_vencimiento()
        self._estado = "Activo"

    def calcular_vencimiento(self):
        return self._estrategia_plazo.calcular(self._fecha_prestamo)

    @property
    def id_solicitud(self):
        return self._id_solicitud

    @property
    def fecha_prestamo(self):
        return self._fecha_prestamo.isoformat()

    @property
    def fecha_vencimiento(self):
        return self._fecha_vencimiento.isoformat()

    @property
    def estado(self):
        return self._estado
