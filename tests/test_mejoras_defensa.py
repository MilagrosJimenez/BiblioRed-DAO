"""Regresiones de las mejoras pedidas para la defensa."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from clases.libro import Libro, normalizar_isbn
from scripts.preparar_demo_reportes import preparar
from servicios.reportes_pdf import crear_grafico


class MejorasDefensaTests(unittest.TestCase):
    def test_isbn_13_valido_y_normalizado(self):
        self.assertEqual(normalizar_isbn("978-0-307-47472-8"), "9780307474728")
        self.assertEqual(Libro(None, "9780307474728", "Título", "Autor", "Editorial").isbn,
                         "9780307474728")

    def test_isbn_incorrectos(self):
        for isbn in ("9788491050293", "123", "ABC123", "9780000000001"):
            with self.subTest(isbn=isbn), self.assertRaises(ValueError):
                normalizar_isbn(isbn)

    def test_cuatro_graficos(self):
        ejemplos = {
            "prestamos": (("Sede", "Activos", "Vencidos", "Días"), [("Centro", 5, 2, 15)]),
            "solicitados": (("Título", "ISBN", "Solicitudes"), [("Libro", "9780307474728", 4)]),
            "disponibilidad": (("Sede", "Título", "Copias", "Libres", "Reservas"),
                               [("Centro", "Libro", 4, 2, 0)]),
            "movimientos": (("Origen", "Destino", "Envíos", "Recibidos", "Promedio"),
                            [("Centro", "Norte", 3, 2, 4.5)]),
        }
        for clave, (columnas, filas) in ejemplos.items():
            with self.subTest(clave=clave):
                self.assertIsNotNone(crear_grafico(clave, columnas, filas))
                self.assertIsNone(crear_grafico(clave, columnas, []))

    def test_base_demo_es_aislada_y_coherente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "solo_reportes.db"
            preparar(ruta)
            with sqlite3.connect(ruta) as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM prestamos").fetchone()[0], 18)
                self.assertGreater(con.execute("SELECT COUNT(*) FROM remitos").fetchone()[0], 0)
                self.assertGreater(con.execute("SELECT COUNT(*) FROM devoluciones").fetchone()[0], 0)
                self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
            with self.assertRaises(FileExistsError):
                preparar(ruta)


if __name__ == "__main__":
    unittest.main()
