
from clases.devolucion import Devolucion
from clases.remito import Remito
from clases.tipos import TipoRemito

from datos.devoluciones_datos import (
    consultar_prestamos_activos,
    consultar_devoluciones,
    registrar_devolucion,
    consultar_pendientes_retorno,
    consultar_remitos_retorno,
    consultar_historial_retorno,
    preparar_retorno,
    avanzar_retorno
)


class DevolucionesServicio:

    def listar_prestamos_activos(self):
        return consultar_prestamos_activos()

    def listar_devoluciones(self):
        return consultar_devoluciones()

    def registrar(self, id_prestamo, estado_fisico, observaciones):
        devolucion = Devolucion(
            id_prestamo, estado_fisico, observaciones
        )

        return registrar_devolucion(devolucion)

    def listar_pendientes_retorno(self):
        return consultar_pendientes_retorno()

    def listar_remitos_retorno(self):
        return consultar_remitos_retorno()

    def consultar_historial(self, id_remito):
        return consultar_historial_retorno(id_remito)

    def empaquetar(self, id_devolucion):
        return preparar_retorno(id_devolucion)

    def avanzar(self, id_remito):
        for datos in consultar_remitos_retorno():
            if datos[0] == id_remito:
                remito = Remito(
                    None, datos[8], datos[9], datos[10], datos[6],
                    tipo=TipoRemito.RETORNO, id_devolucion=datos[1],
                    id_remito=datos[0],
                )

                if remito.estado == "Empaquetado":
                    remito.despachar()

                elif remito.estado == "En tránsito":
                    remito.recibir()

                else:
                    raise ValueError("El remito ya fue recibido")

                return avanzar_retorno(id_remito, remito.estado)

        raise ValueError("No existe el remito seleccionado")
