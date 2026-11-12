"""Pruebas del diseño de los PDF sin usar ni modificar biblioteca.db."""
import tempfile
import unittest
from pathlib import Path

from servicios.reportes_pdf import crear_grafico, construir_pdf


class TestReportesDiseno(unittest.TestCase):
    def test_ceros_sin_grafico_vacio(self):
        columnas = ("Sede", "Activos", "Vencidos", "Máx. días vencido")
        filas = [("Biblioteca Centro", 0, 0, 0), ("Biblioteca Norte", 0, 0, 0)]
        self.assertIsNone(crear_grafico("prestamos", columnas, filas))
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "reporte.pdf"
            construir_pdf("prestamos", "Préstamos activos y vencidos por sede",
                          columnas, filas, destino)
            self.assertTrue(destino.is_file())
            self.assertGreater(destino.stat().st_size, 1000)

    def test_graficos_con_valores_reales(self):
        casos = [
            ("prestamos", ("Sede", "Activos", "Vencidos", "Máx."),
             [("Centro", 5, 2, 3)]),
            ("solicitados", ("Título", "ISBN", "Solicitudes"),
             [("Título", "9780307474728", 8)]),
            ("disponibilidad", ("Sede", "Título", "Copias", "Libres", "Reservas"),
             [("Centro", "Título", 5, 3, 1)]),
            ("movimientos", ("Origen", "Destino", "Envíos", "Recibidos", "Prom."),
             [("Centro", "Norte", 6, 4, 3.2)]),
        ]
        with tempfile.TemporaryDirectory() as carpeta:
            for clave, cabeceras, filas in casos:
                with self.subTest(clave=clave):
                    self.assertIsNotNone(crear_grafico(clave, cabeceras, filas))
                    destino = Path(carpeta) / f"{clave}.pdf"
                    construir_pdf(clave, "Reporte de prueba", cabeceras, filas, destino)
                    self.assertGreater(destino.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
