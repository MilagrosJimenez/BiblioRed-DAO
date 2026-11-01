
class Ejemplar:

    def __init__(self, id_ejemplar, codigo: str,
                 id_libro: int, id_sede: int) -> None:

        if codigo.strip() == "":
            raise ValueError("El código del ejemplar es obligatorio")

        if id_libro <= 0:
            raise ValueError("Debe seleccionar un libro válido")

        if id_sede <= 0:
            raise ValueError("Debe seleccionar una sede válida")

        self._id_ejemplar = id_ejemplar
        self._codigo = codigo.strip()
        self._id_libro = id_libro
        self._id_sede = id_sede
        self._estado = "Disponible"

    @property
    def id_ejemplar(self):
        return self._id_ejemplar

    @property
    def codigo(self):
        return self._codigo

    @property
    def id_libro(self):
        return self._id_libro

    @property
    def id_sede(self):
        return self._id_sede

    @property
    def estado(self):
        return self._estado

    def __str__(self) -> str:
        return f"Ejemplar {self._codigo} - {self._estado}"