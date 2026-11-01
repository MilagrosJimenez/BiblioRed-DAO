
class Remito:

    def __init__(self, id_solicitud: int, id_ejemplar: int,
                 id_sede_origen: int, id_sede_destino: int,
                 estado: str = "Empaquetado") -> None:

        if id_solicitud <= 0 or id_ejemplar <= 0:
            raise ValueError(
                "La solicitud y el ejemplar deben ser válidos"
            )

        if id_sede_origen <= 0 or id_sede_destino <= 0:
            raise ValueError("Las sedes deben ser válidas")

        if id_sede_origen == id_sede_destino:
            raise ValueError(
                "El remito requiere dos sedes distintas"
            )

        if estado not in (
            "Empaquetado",
            "En tránsito",
            "Recibido"
        ):
            raise ValueError("Estado del remito inválido")

        self._id_solicitud = id_solicitud
        self._id_ejemplar = id_ejemplar
        self._id_sede_origen = id_sede_origen
        self._id_sede_destino = id_sede_destino
        self._estado = estado

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
        return self._estado

    def despachar(self) -> None:
        if self._estado != "Empaquetado":
            raise ValueError(
                "Solo se puede despachar un remito empaquetado"
            )

        self._estado = "En tránsito"

    def recibir(self) -> None:
        if self._estado != "En tránsito":
            raise ValueError(
                "Solo se puede recibir un remito en tránsito"
            )

        self._estado = "Recibido"