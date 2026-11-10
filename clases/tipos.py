"""Tipos de valor del UML. Sus valores conservan el formato de SQLite."""
from enum import StrEnum


class TipoRemito(StrEnum):
    IDA = "Ida"
    RETORNO = "Retorno"


class CodigoEstadoRemito(StrEnum):
    EMPAQUETADO = "Empaquetado"
    EN_TRANSITO = "En tránsito"
    RECIBIDO = "Recibido"


class TipoPrestamo(StrEnum):
    LOCAL = "Local"
    INTERBIBLIOTECARIO = "Interbibliotecario"


class EstadoSolicitud(StrEnum):
    PENDIENTE = "Pendiente"
    PENDIENTE_TRASLADO = "Pendiente de traslado"
    EMPAQUETADA = "Empaquetada"
    EN_TRANSITO = "En tránsito"
    RECIBIDA = "Recibida en destino"
    PRESTADA = "Prestada"
    CANCELADA = "Cancelada"


class EstadoPrestamo(StrEnum):
    ACTIVO = "Activo"
    DEVUELTO = "Devuelto"


class EstadoReserva(StrEnum):
    PENDIENTE = "Pendiente"
    ATENDIDA = "Atendida"
    CANCELADA = "Cancelada"


class EstadoFisico(StrEnum):
    BUENO = "Bueno"
    DANADO = "Dañado"


class EstadoEjemplar(StrEnum):
    DISPONIBLE = "Disponible"
    SOLICITADO = "Solicitado"
    EMPAQUETADO = "Empaquetado"
    EN_TRANSITO = "En tránsito"
    RECIBIDO = "Recibido"
    PRESTADO = "Prestado"
    EN_REVISION = "En revisión"
    PENDIENTE_RETORNO = "Pendiente de retorno"
    RETORNO_EMPAQUETADO = "Retorno empaquetado"
    RETORNO_EN_TRANSITO = "Retorno en tránsito"
