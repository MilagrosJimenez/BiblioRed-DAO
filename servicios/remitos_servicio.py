
from clases.remito import Remito

from datos.remitos_datos import (
    consultar_pendientes_traslado,
    consultar_remitos,
    consultar_historial_remito,
    empaquetar_solicitud,
    avanzar_remito
)


class RemitosServicio:

    def listar_pendientes(self):
        return consultar_pendientes_traslado()

    def listar_remitos(self):
        return consultar_remitos()

    def ver_historial(self, id_remito):
        return consultar_historial_remito(id_remito)

    def empaquetar(self, id_solicitud):
        for datos in self.listar_pendientes():

            if datos[0] == id_solicitud:
                remito = Remito(
                    datos[0],
                    datos[5],
                    datos[6],
                    datos[7]
                )

                return empaquetar_solicitud(
                    remito.id_solicitud
                )

        raise ValueError(
            "La solicitud no está pendiente de traslado"
        )

    def cambiar_estado(self, id_remito):
        for datos in self.listar_remitos():

            if datos[0] == id_remito:

                remito = Remito(
                    datos[7],
                    datos[8],
                    datos[9],
                    datos[10],
                    datos[5]
                )

                if remito.estado == "Empaquetado":
                    remito.despachar()

                elif remito.estado == "En tránsito":
                    remito.recibir()

                else:
                    raise ValueError(
                        "El remito ya fue recibido"
                    )

                avanzar_remito(
                    id_remito,
                    remito.estado
                )

                return remito.estado

        raise ValueError("El remito no existe")
