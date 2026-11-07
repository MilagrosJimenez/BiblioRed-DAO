
import flet as ft

from datos.base_datos import (
    crear_tabla_sedes,
    crear_tabla_socios
)

from datos.catalogo_datos import crear_tablas_catalogo
from datos.prestamos_datos import crear_tabla_solicitudes
from datos.remitos_datos import crear_tablas_remitos
from datos.prestamos_efectivos_datos import crear_tabla_prestamos
from datos.devoluciones_datos import crear_tablas_devoluciones
from datos.reservas_datos import crear_tabla_reservas

from interfaces.ventana_completa import VentanaCompleta


def main(page: ft.Page):
    crear_tabla_sedes()
    crear_tabla_socios()
    crear_tablas_catalogo()
    crear_tabla_solicitudes()
    crear_tablas_remitos()
    crear_tabla_prestamos()
    crear_tablas_devoluciones()
    crear_tabla_reservas()

    VentanaCompleta(page)


if __name__ == "__main__":
    ft.run(main)
