from clases.estado_remito import construir_estado


class RemitoRetorno:
    """Contexto State del regreso a la sede propietaria."""

    def __init__(self, id_devolucion: int,
                 estado: str = "Empaquetado") -> None:
        if id_devolucion <= 0:
            raise ValueError("La devolución debe ser válida")
        self._id_devolucion = id_devolucion
        self._estado_actual = construir_estado(estado)

    def _cambiar_estado(self, estado):
        self._estado_actual = estado

    @property
    def id_devolucion(self):
        return self._id_devolucion

    @property
    def estado(self):
        return self._estado_actual.codigo

    def despachar(self):
        self._estado_actual.despachar(self)

    def recibir(self):
        self._estado_actual.recibir(self)
