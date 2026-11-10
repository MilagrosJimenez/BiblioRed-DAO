"""Contrato de las clases y operaciones del PDF entregado, sin tocar SQLite."""
import unittest
from dataclasses import FrozenInstanceError
from datetime import date, datetime

from clases.ejemplar import Ejemplar
from clases.estado_remito import EstadoEnTransito, EstadoRecibido
from clases.estrategia_plazo import EstrategiaPlazo, Plazo21Dias
from clases.historial_remito import HistorialRemito
from clases.prestamo import Prestamo
from clases.remito import Remito
from clases.reserva import Reserva
from clases.sede import Sede
from clases.solicitud_prestamo import SolicitudPrestamo
from clases.tipos import CodigoEstadoRemito, EstadoReserva, TipoRemito


class ContratoUML(unittest.TestCase):
    def test_un_contexto_para_ida_y_retorno(self):
        ida = Remito(1, 1, 1, 2)
        retorno = Remito(None, 1, 2, 1, tipo=TipoRemito.RETORNO, id_devolucion=3)
        self.assertIs(type(ida), type(retorno))
        self.assertEqual(ida.tipo, TipoRemito.IDA)
        self.assertEqual(retorno.tipo, TipoRemito.RETORNO)
        self.assertIsNone(retorno.id_solicitud)
        self.assertIsNone(ida.id_devolucion)

    def test_remito_exige_xor_y_referencia_del_tipo_correcto(self):
        for solicitud, devolucion, tipo in (
            (None, None, TipoRemito.IDA), (1, 2, TipoRemito.IDA),
            (None, 2, TipoRemito.IDA), (1, None, TipoRemito.RETORNO),
            (1, 2, TipoRemito.RETORNO), (None, 0, TipoRemito.RETORNO),
        ):
            with self.subTest(solicitud=solicitud, devolucion=devolucion, tipo=tipo):
                with self.assertRaises(ValueError):
                    Remito(solicitud, 1, 1, 2, tipo=tipo, id_devolucion=devolucion)

    def test_historial_compuesto_con_fechas_y_observaciones(self):
        creacion = datetime(2026, 11, 10, 9)
        salida = datetime(2026, 11, 10, 10)
        llegada = datetime(2026, 11, 10, 11)
        remito = Remito(1, 1, 1, 2, fecha_hora=creacion)
        remito.despachar(salida, "Sale de Centro")
        remito.recibir(llegada, "Llega a Norte")
        self.assertEqual([m.fecha_hora for m in remito.historial_movimientos],
                         [creacion, salida, llegada])
        self.assertIsInstance(remito.historial_movimientos[0], HistorialRemito)
        self.assertEqual(remito.historial_movimientos[-1].observacion, "Llega a Norte")
        self.assertEqual(remito.estado_actual.codigo(), CodigoEstadoRemito.RECIBIDO)
        with self.assertRaises(FrozenInstanceError):
            remito.historial_movimientos[-1].observacion = "Cambio"

    def test_operaciones_invalidas_no_modifican_historial(self):
        remito = Remito(1, 1, 1, 2)
        original = remito.historial_movimientos
        for operacion in (remito.recibir, lambda: remito.cambiar_estado(EstadoRecibido())):
            with self.assertRaises(ValueError):
                operacion()
            self.assertEqual(remito.historial_movimientos, original)
        remito.despachar()
        remito.recibir()
        final = remito.historial_movimientos
        for operacion in (remito.despachar, remito.recibir,
                          lambda: remito.cambiar_estado(EstadoEnTransito())):
            with self.assertRaises(ValueError):
                operacion()
            self.assertEqual(remito.historial_movimientos, final)

    def test_solicitud_genera_un_prestamo_con_strategy(self):
        solicitud = SolicitudPrestamo(1, 1, 1, 1, id_solicitud=5)
        prestamo = solicitud.confirmar_entrega(
            estrategia_plazo=Plazo21Dias(), fecha_entrega=date(2026, 11, 10)
        )
        self.assertIs(solicitud.prestamo, prestamo)
        self.assertEqual(solicitud.estado, "Prestada")
        self.assertEqual(prestamo.fecha_entrega, date(2026, 11, 10))
        self.assertEqual(prestamo.fecha_vencimiento, date(2026, 12, 1))
        with self.assertRaises(ValueError):
            solicitud.confirmar_entrega()

    def test_entrega_interbibliotecaria_requiere_recepcion(self):
        pendiente = SolicitudPrestamo(1, 1, 1, 2, id_solicitud=1)
        with self.assertRaises(ValueError):
            pendiente.confirmar_entrega()
        recibida = SolicitudPrestamo(1, 1, 1, 2, id_solicitud=1,
                                     estado="Recibida en destino")
        self.assertIsInstance(recibida.confirmar_entrega(), Prestamo)

    def test_prestamo_delega_a_estrategia_inyectada(self):
        class PlazoPrueba(EstrategiaPlazo):
            def calcular(self, fecha_entrega):
                return date(2027, 1, 1)

        prestamo = Prestamo(1, estrategia_plazo=PlazoPrueba())
        self.assertEqual(prestamo.calcular_vencimiento(), date(2027, 1, 1))

    def test_prestamo_registra_una_devolucion(self):
        prestamo = Prestamo(1, id_prestamo=8)
        with self.assertRaises(ValueError):
            prestamo.registrar_devolucion("Incorrecto")
        self.assertEqual(prestamo.estado, "Activo")
        devolucion = prestamo.registrar_devolucion("Dañado", "Tapa rota")
        self.assertIs(prestamo.devolucion, devolucion)
        self.assertEqual(devolucion.id_prestamo, 8)
        self.assertEqual(devolucion.fecha, date.today())
        self.assertEqual(prestamo.estado, "Devuelto")
        with self.assertRaises(ValueError):
            prestamo.registrar_devolucion("Bueno")

    def test_reserva_tiene_fecha_y_operaciones_terminales(self):
        for operacion, esperado in (("atender", EstadoReserva.ATENDIDA),
                                   ("cancelar", EstadoReserva.CANCELADA)):
            reserva = Reserva(1, 1, 2, id_reserva=4, fecha=date(2026, 11, 10))
            self.assertEqual(reserva.fecha, date(2026, 11, 10))
            self.assertEqual(reserva.id_sede_destino, 2)
            getattr(reserva, operacion)()
            self.assertEqual(reserva.estado, esperado)
            for siguiente in (reserva.atender, reserva.cancelar):
                with self.assertRaises(ValueError):
                    siguiente()

    def test_propiedad_y_ubicacion_no_se_confunden(self):
        ejemplar = Ejemplar(1, "E-1", 1, 1, id_sede_actual=2, estado="Recibido")
        self.assertEqual(ejemplar.id_sede_propietaria, 1)
        self.assertEqual(ejemplar.id_sede_actual, 2)
        self.assertEqual(Ejemplar(2, "E-2", 1, 1).id_sede_actual, 1)

    def test_contacto_sede(self):
        sede = Sede(1, "Centro", "Dirección", "123", "8-18")
        self.assertEqual(sede.contacto, "123")
