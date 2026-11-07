from clases.estado_remito import construir_estado


class Remito:
    """Contexto State del traslado de ida."""

    def __init__(self, id_solicitud: int, id_ejemplar: int,
                 id_sede_origen: int, id_sede_destino: int,
                 estado: str = "Empaquetado") -> None:

        if id_solicitud <= 0 or id_ejemplar <= 0:
            raise ValueError("La solicitud y el ejemplar deben ser válidos")
        if id_sede_origen <= 0 or id_sede_destino <= 0:
            raise ValueError("Las sedes deben ser válidas")
        if id_sede_origen == id_sede_destino:
            raise ValueError("El remito requiere dos sedes distintas")

        self._id_solicitud = id_solicitud
        self._id_ejemplar = id_ejemplar
        self._id_sede_origen = id_sede_origen
        self._id_sede_destino = id_sede_destino
        self._estado_actual = construir_estado(estado)

    def _cambiar_estado(self, estado):
        self._estado_actual = estado

    @property
    def id_solicitud(self):
        return self._id_solicitud

    @property
    def id_ejemplar(self):
        return self._id_ejemplar

    @property
    def id_sede_origen(self):
        return self._id_sede_origen

    @property
    def id_sede_destino(self):
        return self._id_sede_destino

    @property
    def estado(self):
        return self._estado_actual.codigo

    def despachar(self):
        self._estado_actual.despachar(self)

    def recibir(self):
        self._estado_actual.recibir(self)
