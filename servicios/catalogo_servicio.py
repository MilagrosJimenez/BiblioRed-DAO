
from clases.libro import Libro
from clases.ejemplar import Ejemplar

from datos.base_datos import consultar_sedes

from datos.catalogo_datos import (
    guardar_libro,
    consultar_libros,
    actualizar_libro,
    guardar_ejemplar,
    consultar_ejemplares
)


class CatalogoServicio:

    def listar_libros(self):
        return consultar_libros()

    def listar_ejemplares(self):
        return consultar_ejemplares()

    def listar_sedes_activas(self):
        sedes_activas = []

        for sede in consultar_sedes():
            if sede[5] == 1:
                sedes_activas.append(sede)

        return sedes_activas

    def registrar_libro(self, isbn, titulo, autor, editorial):
        libro = Libro(None, isbn, titulo, autor, editorial)

        if not guardar_libro(libro):
            raise ValueError("Ya existe un libro con ese ISBN")

    def modificar_libro(self, id_libro, isbn, titulo, autor,
                        editorial):
        libro = Libro(
            id_libro, isbn, titulo, autor, editorial
        )

        actualizar_libro(libro)

    def registrar_ejemplar(self, codigo, id_libro, id_sede):
        libro_encontrado = False
        sede_activa = False

        for libro in consultar_libros():
            if libro[0] == id_libro:
                libro_encontrado = True

        for sede in self.listar_sedes_activas():
            if sede[0] == id_sede:
                sede_activa = True

        if not libro_encontrado:
            raise ValueError(
                "El libro seleccionado no existe"
            )

        if not sede_activa:
            raise ValueError(
                "La sede no existe o está dada de baja"
            )

        ejemplar = Ejemplar(
            None, codigo, id_libro, id_sede
        )

        if not guardar_ejemplar(ejemplar):
            raise ValueError(
                "Ya existe un ejemplar con ese código"
            )
