
class RemitoRetorno:
    def __init__(self, id_devolucion: int,
                 estado: str = "Empaquetado") -> None:

        if id_devolucion <= 0:
            raise ValueError("La devolución debe ser válida")

        if estado not in ("Empaquetado", "En tránsito", "Recibido"):
            raise ValueError("Estado del remito inválido")

        self._id_devolucion = id_devolucion
        self._estado = estado

    @property
    def id_devolucion(self):
        return self._id_devolucion

    @property
    def estado(self):
        return self._estado

    def despachar(self) -> None:
        if self._estado != "Empaquetado":
            raise ValueError("El remito no está empaquetado")

        self._estado = "En tránsito"

    def recibir(self) -> None:
        if self._estado != "En tránsito":
            raise ValueError("El remito no está en tránsito")

        self._estado = "Recibido"
