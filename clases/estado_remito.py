"""Patrón State. Reglas del ciclo de vida compartidas por ida y retorno."""
from abc import ABC, abstractmethod


class EstadoRemito(ABC):
    @property
    @abstractmethod
    def codigo(self):
        """Estado persistido en SQLite."""

    def despachar(self, contexto):
        raise ValueError("Solo se puede despachar un remito empaquetado")

    def recibir(self, contexto):
        raise ValueError("Solo se puede recibir un remito en tránsito")


class EstadoEmpaquetado(EstadoRemito):
    @property
    def codigo(self):
        return "Empaquetado"

    def despachar(self, contexto):
        contexto._cambiar_estado(EstadoEnTransito())


class EstadoEnTransito(EstadoRemito):
    @property
    def codigo(self):
        return "En tránsito"

    def recibir(self, contexto):
        contexto._cambiar_estado(EstadoRecibido())


class EstadoRecibido(EstadoRemito):
    @property
    def codigo(self):
        return "Recibido"


def construir_estado(codigo):
    estados = {
        "Empaquetado": EstadoEmpaquetado,
        "En tránsito": EstadoEnTransito,
        "Recibido": EstadoRecibido,
    }
    if codigo not in estados:
        raise ValueError("Estado del remito inválido")
    return estados[codigo]()
