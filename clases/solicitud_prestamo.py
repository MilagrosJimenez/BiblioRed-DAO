
class SolicitudPrestamo:

    def __init__(self, id_socio: int, id_ejemplar: int,
                 id_sede_origen: int, id_sede_destino: int) -> None:

        if id_socio <= 0 or id_ejemplar <= 0:
            raise ValueError("Debe seleccionar un socio y un ejemplar válidos")

        if id_sede_origen <= 0 or id_sede_destino <= 0:
            raise ValueError("Las sedes de origen y destino deben ser válidas")

        self._id_socio = id_socio
        self._id_ejemplar = id_ejemplar
        self._id_sede_origen = id_sede_origen
        self._id_sede_destino = id_sede_destino

        if id_sede_origen == id_sede_destino:
            self._tipo = "Local"
            self._estado = "Pendiente"
        else:
            self._tipo = "Interbibliotecario"
            self._estado = "Pendiente de traslado"

    @property
    def id_socio(self):
        return self._id_socio

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
    def tipo(self):
        return self._tipo

    @property
    def estado(self):
        return self._estado
