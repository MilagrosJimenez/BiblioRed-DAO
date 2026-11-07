
from clases.solicitud_prestamo import SolicitudPrestamo

from datos.base_datos import consultar_sedes, consultar_socios
from datos.prestamos_datos import consultar_ejemplares_solicitables

from datos.prestamos_datos import (
    consultar_solicitudes,
    guardar_solicitud,
    cancelar_solicitud
)


class PrestamosServicio:

    def listar_socios_habilitados(self):
        socios = []

        for socio in consultar_socios():
            if socio[6] == 1:
                socios.append(socio)

        return socios

    def listar_sedes_activas(self):
        sedes = []

        for sede in consultar_sedes():
            if sede[5] == 1:
                sedes.append(sede)

        return sedes

    def listar_ejemplares_disponibles(self):
        return consultar_ejemplares_solicitables()

    def listar_solicitudes(self):
        return consultar_solicitudes()

    def registrar(self, id_socio, id_ejemplar, id_destino):
        socio_valido = False
        ejemplar_elegido = None
        destino_valido = False

        for socio in self.listar_socios_habilitados():
            if socio[0] == id_socio:
                socio_valido = True

        for ejemplar in self.listar_ejemplares_disponibles():
            if ejemplar[0] == id_ejemplar:
                ejemplar_elegido = ejemplar

        for sede in self.listar_sedes_activas():
            if sede[0] == id_destino:
                destino_valido = True

        if not socio_valido:
            raise ValueError(
                "El socio no existe o está inhabilitado"
            )

        if ejemplar_elegido is None:
            raise ValueError(
                "El ejemplar no está disponible en una sede activa"
            )

        if not destino_valido:
            raise ValueError(
                "La sede destino no existe o está dada de baja"
            )

        # La sede origen se obtiene del ejemplar.
        id_origen = ejemplar_elegido[7]

        solicitud = SolicitudPrestamo(
            id_socio,
            id_ejemplar,
            id_origen,
            id_destino
        )

        guardar_solicitud(solicitud)

        return solicitud.tipo

    def cancelar(self, id_solicitud):
        cancelar_solicitud(id_solicitud)
