"""Patrón State. Reglas del ciclo de vida compartidas por ida y retorno."""
from abc import ABC, abstractmethod
from clases.tipos import CodigoEstadoRemito


class EstadoRemito(ABC):
    @abstractmethod
    def codigo(self):
        """Estado persistido en SQLite."""

    def despachar(self, contexto, fecha_hora=None, observacion=""):
        raise ValueError("Solo se puede despachar un remito empaquetado")

    def recibir(self, contexto, fecha_hora=None, observacion=""):
        raise ValueError("Solo se puede recibir un remito en tránsito")


class EstadoEmpaquetado(EstadoRemito):
    def codigo(self):
        return CodigoEstadoRemito.EMPAQUETADO

    def despachar(self, contexto, fecha_hora=None, observacion=""):
        contexto.cambiar_estado(EstadoEnTransito(), fecha_hora, observacion)


class EstadoEnTransito(EstadoRemito):
    def codigo(self):
        return CodigoEstadoRemito.EN_TRANSITO

    def recibir(self, contexto, fecha_hora=None, observacion=""):
        contexto.cambiar_estado(EstadoRecibido(), fecha_hora, observacion)


class EstadoRecibido(EstadoRemito):
    def codigo(self):
        return CodigoEstadoRemito.RECIBIDO


def construir_estado(codigo):
    estados = {
        "Empaquetado": EstadoEmpaquetado,
        "En tránsito": EstadoEnTransito,
        "Recibido": EstadoRecibido,
    }
    if codigo not in estados:
        raise ValueError("Estado del remito inválido")
    return estados[codigo]()
