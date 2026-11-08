"""El buscador de Inicio navega por las 12 secciones del menú lateral."""
import unittest

from interfaces.busqueda_general import buscar_secciones


SECCIONES = [
    "Inicio",
    "Administrar sedes",
    "Administrar socios",
    "Catálogo y ejemplares",
    "Solicitudes de préstamo",
    "Remitos y traslados",
    "Préstamos efectivos",
    "Devoluciones",
    "Reservas y disponibilidad",
    "Inventario por códigos",
    "Historial de lecturas",
    "Reportes",
]


class PruebasBusquedaDeSecciones(unittest.TestCase):
    def test_filtra_por_fragmentos(self):
        self.assertEqual(
            buscar_secciones("soc", SECCIONES),
            ["Administrar socios"],
        )
        self.assertEqual(
            buscar_secciones("sed", SECCIONES),
            ["Administrar sedes"],
        )

    def test_ignora_mayusculas_y_tildes(self):
        self.assertEqual(
            buscar_secciones("CATALOGO", SECCIONES),
            ["Catálogo y ejemplares"],
        )
        self.assertEqual(
            buscar_secciones("prestamo", SECCIONES),
            ["Solicitudes de préstamo", "Préstamos efectivos"],
        )

    def test_incluye_todos_los_modulos_del_menu(self):
        self.assertEqual(buscar_secciones("report", SECCIONES), ["Reportes"])
        self.assertEqual(
            buscar_secciones("reserv", SECCIONES),
            ["Reservas y disponibilidad"],
        )
        self.assertEqual(
            buscar_secciones("devol", SECCIONES),
            ["Devoluciones"],
        )

    def test_no_busca_documentos_ni_registros(self):
        self.assertEqual(buscar_secciones("99001234", SECCIONES), [])
        self.assertEqual(buscar_secciones("biblioteca centro", SECCIONES), [])

    def test_vacio_limite_y_sin_coincidencias(self):
        self.assertEqual(buscar_secciones("", SECCIONES), [])
        self.assertEqual(buscar_secciones("  ", SECCIONES), [])
        self.assertEqual(buscar_secciones("zzzzz", SECCIONES), [])
        self.assertEqual(buscar_secciones("administrar", SECCIONES, limite=1),
                         ["Administrar sedes"])
        self.assertEqual(buscar_secciones("administrar", SECCIONES, limite=0), [])


if __name__ == "__main__":
    unittest.main()
