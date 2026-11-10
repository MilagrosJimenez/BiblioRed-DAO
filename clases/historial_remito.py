"""Movimiento compuesto por Remito, según el diagrama entregado."""
from dataclasses import dataclass
from datetime import datetime

from clases.tipos import CodigoEstadoRemito


@dataclass(frozen=True)
class HistorialRemito:
    estado: CodigoEstadoRemito
    fecha_hora: datetime
    observacion: str = ""
    id_movimiento: int | None = None
