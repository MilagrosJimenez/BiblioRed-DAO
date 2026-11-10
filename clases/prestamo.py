from datetime import date
from clases.estrategia_plazo import seleccionar_estrategia
from clases.tipos import EstadoPrestamo


class Prestamo:
    """Préstamo que delega el vencimiento a una estrategia intercambiable."""

    def __init__(self, id_solicitud: int, plazo_dias: int = 14, *,
                 id_prestamo=None, fecha_entrega=None, estrategia_plazo=None,
                 estado=EstadoPrestamo.ACTIVO, fecha_vencimiento=None) -> None:
        if id_solicitud <= 0:
            raise ValueError("Debe seleccionar una solicitud válida")

        self._id_solicitud = id_solicitud
        self._id_prestamo = id_prestamo
        self._fecha_entrega = fecha_entrega or date.today()
        self._estrategia_plazo = estrategia_plazo or seleccionar_estrategia(plazo_dias)
        self._fecha_vencimiento = fecha_vencimiento or self.calcular_vencimiento()
        self._estado = EstadoPrestamo(estado)
        self._devolucion = None

    def calcular_vencimiento(self):
        return self._estrategia_plazo.calcular(self._fecha_entrega)

    def registrar_devolucion(self, estado_fisico, observaciones=""):
        from clases.devolucion import Devolucion

        if self._estado != EstadoPrestamo.ACTIVO:
            raise ValueError("El préstamo ya fue devuelto o no está activo")
        if self._id_prestamo is None:
            raise ValueError("El préstamo debe estar registrado antes de devolverlo")
        devolucion = Devolucion(self._id_prestamo, estado_fisico, observaciones)
        self._devolucion = devolucion
        self._estado = EstadoPrestamo.DEVUELTO
        return devolucion

    @property
    def id_prestamo(self):
        return self._id_prestamo

    @property
    def fecha_entrega(self):
        return self._fecha_entrega

    @property
    def estrategia_plazo(self):
        return self._estrategia_plazo

    @property
    def devolucion(self):
        return self._devolucion

    @property
    def id_solicitud(self):
        return self._id_solicitud

    @property
    def fecha_prestamo(self):
        """Nombre histórico de la columna SQLite; en el UML es fecha_entrega."""
        return self._fecha_entrega.isoformat()

    @property
    def fecha_vencimiento(self):
        return self._fecha_vencimiento

    @property
    def estado(self):
        return self._estado
