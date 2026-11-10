
class Sede:

    def __init__(self, id_sede: int, nombre: str, direccion: str,
                 telefono: str, horarios: str) -> None:

        if id_sede <= 0:
            raise ValueError("El ID debe ser mayor a cero")

        if nombre == "":
            raise ValueError("El nombre es obligatorio")

        if direccion == "":
            raise ValueError("La dirección es obligatoria")

        if telefono == "":
            raise ValueError("El teléfono es obligatorio")

        if horarios == "":
            raise ValueError("Los horarios son obligatorios")

        self._id_sede = id_sede
        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._horarios = horarios
        self._activa = True

    @property
    def contacto(self) -> str:
        """Contacto de la sede, almacenado como teléfono en SQLite."""
        return self._telefono

    @property
    def id_sede(self) -> int:
        return self._id_sede

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def direccion(self) -> str:
        return self._direccion

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def horarios(self) -> str:
        return self._horarios

    @property
    def activa(self) -> bool:
        return self._activa

    def actualizar_datos(self, nombre: str, direccion: str,
                         telefono: str, horarios: str) -> None:

        if nombre == "" or direccion == "":
            raise ValueError("Nombre y dirección son obligatorios")

        if telefono == "" or horarios == "":
            raise ValueError("Teléfono y horarios son obligatorios")

        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._horarios = horarios

    def dar_de_baja(self) -> None:
        self._activa = False

    def reactivar(self) -> None:
        self._activa = True

    def __str__(self) -> str:
        estado = "Activa" if self._activa else "Dada de baja"
        return f"Sede {self._id_sede}: {self._nombre} - {estado}"
