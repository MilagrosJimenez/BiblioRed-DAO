
from clases.devolucion import Devolucion
from clases.remito_retorno import RemitoRetorno

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
        remito = RemitoRetorno(id_devolucion)
        return preparar_retorno(remito.id_devolucion)

    def avanzar(self, id_remito):
        for datos in consultar_remitos_retorno():
            if datos[0] == id_remito:
                remito = RemitoRetorno(datos[1], datos[6])

                if remito.estado == "Empaquetado":
                    remito.despachar()

                elif remito.estado == "En tránsito":
                    remito.recibir()

                else:
                    raise ValueError("El remito ya fue recibido")

                return avanzar_retorno(id_remito, remito.estado)

        raise ValueError("No existe el remito seleccionado")
