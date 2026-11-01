
class Socio:

    def __init__(self, id_socio, documento: str, nombre: str,
                 apellido: str, telefono: str, correo: str,
                 habilitado: bool = True) -> None:

        if id_socio is not None and id_socio <= 0:
            raise ValueError("El ID del socio debe ser positivo")

        if documento == "" or not documento.isnumeric():
            raise ValueError("El documento debe contener solamente números")

        if nombre.strip() == "" or apellido.strip() == "":
            raise ValueError("El nombre y el apellido son obligatorios")

        if telefono.strip() == "":
            raise ValueError("El teléfono es obligatorio")

        if correo != "" and "@" not in correo:
            raise ValueError("El correo debe contener @")

        self._id_socio = id_socio
        self._documento = documento
        self._nombre = nombre
        self._apellido = apellido
        self._telefono = telefono
        self._correo = correo
        self._habilitado = habilitado

    @property
    def id_socio(self):
        return self._id_socio

    @property
    def documento(self):
        return self._documento

    @property
    def nombre(self):
        return self._nombre

    @property
    def apellido(self):
        return self._apellido

    @property
    def telefono(self):
        return self._telefono

    @property
    def correo(self):
        return self._correo

    @property
    def habilitado(self):
        return self._habilitado

    def actualizar_datos(self, nombre: str, apellido: str,
                         telefono: str, correo: str) -> None:

        if nombre.strip() == "" or apellido.strip() == "":
            raise ValueError("El nombre y el apellido son obligatorios")

        if telefono.strip() == "":
            raise ValueError("El teléfono es obligatorio")

        if correo != "" and "@" not in correo:
            raise ValueError("El correo debe contener @")

        self._nombre = nombre
        self._apellido = apellido
        self._telefono = telefono
        self._correo = correo

    def inhabilitar(self) -> None:
        self._habilitado = False

    def habilitar(self) -> None:
        self._habilitado = True

    def __str__(self) -> str:
        estado = "Habilitado" if self._habilitado else "Inhabilitado"

        return f"{self._apellido}, {self._nombre} - {estado}"