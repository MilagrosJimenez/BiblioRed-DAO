"""El buscador global debe trabajar sobre datos reales sin modificar SQLite."""
import unittest
from unittest.mock import patch

from interfaces.busqueda_general import buscar_en_bibliored


class PruebasBusquedaGlobal(unittest.TestCase):
    def setUp(self):
        datos = {
            "consultar_sedes": [
                (9001, "Biblioteca Prueba DAO", "Calle Centro 100",
                 "351", "Lunes a viernes", 1)
            ],
            "consultar_socios": [
                (1, "99001234", "Lucía", "Torres", "351", "", 1)
            ],
            "consultar_libros": [
                (1, "9780000000001", "Ingeniería de objetos",
                 "Autora Prueba", "Editorial", 1, 1)
            ],
            "consultar_ejemplares": [
                (1, "EJ-001", "Ingeniería de objetos", "9780000000001",
                 "Biblioteca Prueba DAO", "Disponible", 1, 9001,
                 "Biblioteca Prueba DAO")
            ],
            "consultar_solicitudes": [
                (2, "Torres, Lucía", "99001234", "EJ-001", "Ingeniería de objetos",
                 "Biblioteca Prueba DAO", "Biblioteca Norte",
                 "Interbibliotecario", "Pendiente de traslado", "2026-11-07")
            ],
            "consultar_remitos": [
                (4, "EJ-001", "Ingeniería de objetos", "Biblioteca Prueba DAO",
                 "Biblioteca Norte", "En tránsito", "2026-11-07",
                 2, 1, 9001, 9002)
            ],
        }
        self.parches = [
            patch("interfaces.busqueda_general." + nombre, return_value=filas)
            for nombre, filas in datos.items()
        ]
        for p in self.parches:
            p.start()

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()

    def test_busca_por_nombre_con_tilde_ignorada(self):
        encontrados = buscar_en_bibliored("lucia")
        self.assertTrue(any(r["tipo"] == "Socio" for r in encontrados))
        self.assertTrue(any(r["tipo"] == "Solicitud" for r in encontrados))

    def test_busca_por_digito_en_identificadores(self):
        encontrados = buscar_en_bibliored("9001")
        self.assertTrue(any(r["tipo"] == "Sede" for r in encontrados))
        encontrados = buscar_en_bibliored("EJ-001")
        self.assertTrue(any(r["tipo"] == "Ejemplar" for r in encontrados))
        self.assertTrue(any(r["tipo"] == "Remito" for r in encontrados))

    def test_cadena_vacia_no_hace_busqueda(self):
        self.assertEqual(buscar_en_bibliored(""), [])
        for p in self.parches:
            p.assert_not_called()

    def test_limite_y_destinos(self):
        resultados = buscar_en_bibliored("biblioteca", limite=3)
        self.assertLessEqual(len(resultados), 3)
        self.assertTrue(all(
            r["destino"] in (
                "Administrar sedes", "Administrar socios", "Catálogo y ejemplares",
                "Solicitudes de préstamo", "Remitos y traslados"
            ) for r in resultados
        ))


if __name__ == "__main__":
    unittest.main()
