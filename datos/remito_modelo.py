"""Mapeo de las tablas históricas de ida/retorno al único Remito del UML."""
from datetime import datetime

from clases.historial_remito import HistorialRemito
from clases.remito import Remito
from clases.tipos import CodigoEstadoRemito, TipoRemito


def cargar_remito(cursor, id_remito, tipo):
    tipo = TipoRemito(tipo)
    if tipo == TipoRemito.IDA:
        tabla, historial, referencia = "remitos", "historial_remitos", "id_solicitud"
    else:
        tabla, historial, referencia = "remitos_retorno", "historial_retornos", "id_devolucion"
    # Los identificadores SQL provienen exclusivamente de las constantes anteriores.
    cursor.execute(f"""
        SELECT {referencia}, id_ejemplar, id_sede_origen, id_sede_destino, estado
        FROM {tabla} WHERE id_remito = ?
    """, (id_remito,))
    datos = cursor.fetchone()
    if datos is None:
        raise ValueError("El remito no existe")
    cursor.execute(f"""
        SELECT id_historial, estado, fecha, observacion
        FROM {historial} WHERE id_remito = ? ORDER BY id_historial
    """, (id_remito,))
    movimientos = [
        HistorialRemito(CodigoEstadoRemito(estado), datetime.fromisoformat(fecha),
                        observacion, id_movimiento)
        for id_movimiento, estado, fecha, observacion in cursor.fetchall()
    ]
    return Remito(
        datos[0] if tipo == TipoRemito.IDA else None,
        datos[1], datos[2], datos[3], datos[4], tipo=tipo,
        id_devolucion=datos[0] if tipo == TipoRemito.RETORNO else None,
        id_remito=id_remito, historial_movimientos=movimientos,
    )
