"""Patrón Strategy para los vencimientos de préstamos."""
from abc import ABC, abstractmethod
from datetime import timedelta


class EstrategiaPlazo(ABC):
    @abstractmethod
    def calcular(self, fecha_entrega):
        """Devuelve fecha de vencimiento a partir de la entrega."""


class Plazo7Dias(EstrategiaPlazo):
    def calcular(self, fecha_entrega):
        return fecha_entrega + timedelta(days=7)


class Plazo14Dias(EstrategiaPlazo):
    def calcular(self, fecha_entrega):
        return fecha_entrega + timedelta(days=14)


class Plazo21Dias(EstrategiaPlazo):
    def calcular(self, fecha_entrega):
        return fecha_entrega + timedelta(days=21)


def seleccionar_estrategia(plazo_dias):
    estrategias = {
        7: Plazo7Dias,
        14: Plazo14Dias,
        21: Plazo21Dias,
    }
    if plazo_dias not in estrategias:
        raise ValueError("El plazo debe ser de 7, 14 o 21 días")
    return estrategias[plazo_dias]()
