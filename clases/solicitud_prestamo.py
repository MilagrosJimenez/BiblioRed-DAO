
from clases.tipos import EstadoSolicitud, TipoPrestamo


class SolicitudPrestamo:

    def __init__(self, id_socio: int, id_ejemplar: int,
                 id_sede_origen: int, id_sede_destino: int, *,
                 id_solicitud=None, estado=None) -> None:

        if id_socio <= 0 or id_ejemplar <= 0:
            raise ValueError("Debe seleccionar un socio y un ejemplar válidos")

        if id_sede_origen <= 0 or id_sede_destino <= 0:
            raise ValueError("Las sedes de origen y destino deben ser válidas")

        self._id_socio = id_socio
        self._id_solicitud = id_solicitud
        self._prestamo = None
        self._id_ejemplar = id_ejemplar
        self._id_sede_origen = id_sede_origen
        self._id_sede_destino = id_sede_destino

        if id_sede_origen == id_sede_destino:
            self._tipo = TipoPrestamo.LOCAL
            self._estado = EstadoSolicitud.PENDIENTE
        else:
            self._tipo = TipoPrestamo.INTERBIBLIOTECARIO
            self._estado = EstadoSolicitud.PENDIENTE_TRASLADO

        if estado is not None:
            self._estado = EstadoSolicitud(estado)

    def confirmar_entrega(self, plazo_dias=14, *, estrategia_plazo=None,
                          fecha_entrega=None):
        from clases.prestamo import Prestamo

        esperado = (EstadoSolicitud.PENDIENTE if self._tipo == TipoPrestamo.LOCAL
                    else EstadoSolicitud.RECIBIDA)
        if self._estado != esperado or self._prestamo is not None:
            raise ValueError("La solicitud no está lista para entregar")
        if self._id_solicitud is None:
            raise ValueError("La solicitud debe estar registrada antes de entregar")
        prestamo = Prestamo(self._id_solicitud, plazo_dias,
                            estrategia_plazo=estrategia_plazo,
                            fecha_entrega=fecha_entrega)
        self._prestamo = prestamo
        self._estado = EstadoSolicitud.PRESTADA
        return prestamo

    @property
    def id_solicitud(self):
        return self._id_solicitud

    @property
    def prestamo(self):
        return self._prestamo

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
