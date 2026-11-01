
from datetime import date, timedelta


class Prestamo:

    def __init__(self, id_solicitud: int, plazo_dias: int) -> None:

        if id_solicitud <= 0:
            raise ValueError("Debe seleccionar una solicitud válida")

        if plazo_dias not in (7, 14, 21):
            raise ValueError("El plazo debe ser de 7, 14 o 21 días")

        self._id_solicitud = id_solicitud
        self._fecha_prestamo = date.today()
        self._fecha_vencimiento = self._fecha_prestamo + timedelta(
            days=plazo_dias
        )
        self._estado = "Activo"

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
