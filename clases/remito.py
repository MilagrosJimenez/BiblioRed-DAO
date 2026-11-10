from datetime import datetime

from clases.estado_remito import EstadoRemito, construir_estado
from clases.historial_remito import HistorialRemito
from clases.tipos import TipoRemito


class Remito:
    """Único contexto State para traslados de ida y de retorno (UML)."""

    def __init__(self, id_solicitud: int | None, id_ejemplar: int,
                 id_sede_origen: int, id_sede_destino: int,
                 estado: str = "Empaquetado", *, tipo=TipoRemito.IDA,
                 id_devolucion=None, id_remito=None, fecha_hora=None,
                 historial_movimientos=None) -> None:

        tipo = TipoRemito(tipo)
        if tipo == TipoRemito.IDA:
            valido = id_solicitud is not None and id_solicitud > 0 and id_devolucion is None
        else:
            valido = id_devolucion is not None and id_devolucion > 0 and id_solicitud is None
        if not valido:
            raise ValueError("El remito debe tener una solicitud de ida O una devolución de retorno")
        if id_ejemplar <= 0:
            raise ValueError("El ejemplar debe ser válido")
        if id_sede_origen <= 0 or id_sede_destino <= 0:
            raise ValueError("Las sedes deben ser válidas")
        if id_sede_origen == id_sede_destino:
            raise ValueError("El remito requiere dos sedes distintas")

        self._id_solicitud = id_solicitud
        self._id_devolucion = id_devolucion
        self._id_remito = id_remito
        self._tipo = tipo
        self._id_ejemplar = id_ejemplar
        self._id_sede_origen = id_sede_origen
        self._id_sede_destino = id_sede_destino
        self._estado_actual = construir_estado(estado)
        observacion_inicial = ("Ejemplar preparado para despacho" if tipo == TipoRemito.IDA
                               else "Devolución preparada para retorno")
        self._historial_movimientos = (
            list(historial_movimientos) if historial_movimientos is not None else [
                HistorialRemito(self.estado, fecha_hora or datetime.now(), observacion_inicial)
            ]
        )
        if not self._historial_movimientos or self._historial_movimientos[-1].estado != self.estado:
            raise ValueError("El historial debe contener el estado actual del remito")

    def cambiar_estado(self, nuevo: EstadoRemito, fecha_hora=None, observacion=""):
        permitidos = {"Empaquetado": "En tránsito", "En tránsito": "Recibido"}
        if not isinstance(nuevo, EstadoRemito) or permitidos.get(self.estado) != nuevo.codigo():
            raise ValueError("Cambio de estado de remito no permitido")
        movimiento = HistorialRemito(nuevo.codigo(), fecha_hora or datetime.now(), observacion)
        self._estado_actual = nuevo
        self._historial_movimientos.append(movimiento)

    @property
    def id_remito(self):
        return self._id_remito

    @property
    def tipo(self):
        return self._tipo

    @property
    def id_devolucion(self):
        return self._id_devolucion

    @property
    def historial_movimientos(self):
        return tuple(self._historial_movimientos)

    @property
    def estado_actual(self):
        return self._estado_actual

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
        return self._estado_actual.codigo()

    def despachar(self, fecha_hora=None, observacion=""):
        self._estado_actual.despachar(self, fecha_hora, observacion)

    def recibir(self, fecha_hora=None, observacion=""):
        self._estado_actual.recibir(self, fecha_hora, observacion)
