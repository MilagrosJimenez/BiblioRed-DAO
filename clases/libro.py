
def normalizar_isbn(isbn: str) -> str:
    """Validar el dígito de control ISBN-13 y normalizar espacios/guiones."""
    valor = isbn.replace("-", "").replace(" ", "")
    if len(valor) != 13 or not valor.isascii() or not valor.isdigit():
        raise ValueError("El ISBN debe tener exactamente 13 dígitos")
    suma = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(valor))
    if suma % 10:
        raise ValueError("El ISBN-13 tiene un dígito de control inválido")
    return valor


class Libro:

    def __init__(self, id_libro, isbn: str, titulo: str,
                 autor: str, editorial: str) -> None:

        isbn = normalizar_isbn(isbn)

        if titulo.strip() == "":
            raise ValueError("El título es obligatorio")

        if autor.strip() == "":
            raise ValueError("El autor es obligatorio")

        if editorial.strip() == "":
            raise ValueError("La editorial es obligatoria")

        self._id_libro = id_libro
        self._isbn = isbn
        self._titulo = titulo.strip()
        self._autor = autor.strip()
        self._editorial = editorial.strip()

    @property
    def id_libro(self):
        return self._id_libro

    @property
    def isbn(self):
        return self._isbn

    @property
    def titulo(self):
        return self._titulo

    @property
    def autor(self):
        return self._autor

    @property
    def editorial(self):
        return self._editorial

    def actualizar_datos(self, titulo: str, autor: str,
                         editorial: str) -> None:

        if titulo.strip() == "" or autor.strip() == "":
            raise ValueError("El título y el autor son obligatorios")

        if editorial.strip() == "":
            raise ValueError("La editorial es obligatoria")

        self._titulo = titulo.strip()
        self._autor = autor.strip()
        self._editorial = editorial.strip()

    def __str__(self) -> str:
        return f"{self._titulo} - {self._autor}"