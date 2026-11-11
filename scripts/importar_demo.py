"""Importa datos ficticios sin borrar ni actualizar registros existentes."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from datos.base_datos import RUTA_BASE_DATOS, crear_tabla_sedes, crear_tabla_socios
from datos.catalogo_datos import crear_tablas_catalogo
from datos.prestamos_datos import crear_tabla_solicitudes
from datos.remitos_datos import crear_tablas_remitos
from datos.prestamos_efectivos_datos import crear_tabla_prestamos
from datos.devoluciones_datos import crear_tablas_devoluciones
from datos.reservas_datos import crear_tabla_reservas


CARPETA_DEMO = Path(__file__).resolve().parents[1] / "datos_demo"
CAMPOS = {
    "sedes": ("id_sede", "nombre", "direccion", "telefono", "horarios", "activa"),
    "socios": ("documento", "nombre", "apellido", "telefono", "correo", "habilitado"),
    "libros": ("isbn", "titulo", "autor", "editorial"),
    "ejemplares": ("codigo", "isbn", "id_sede"),
}


def leer_datos(carpeta):
    datos = {}
    for tabla, campos in CAMPOS.items():
        archivo = Path(carpeta) / f"{tabla}.json"
        with archivo.open(encoding="utf-8") as entrada:
            filas = json.load(entrada)
        if not isinstance(filas, list):
            raise ValueError(f"{archivo.name}: se esperaba una lista")
        claves = set()
        for numero, fila in enumerate(filas, 1):
            contexto = f"{archivo.name}, registro {numero}"
            if not isinstance(fila, dict) or set(fila) != set(campos):
                raise ValueError(f"{contexto}: campos esperados: {', '.join(campos)}")
            for campo, valor in fila.items():
                if campo == "id_sede":
                    valido = type(valor) is int and valor > 0
                elif campo in ("activa", "habilitado"):
                    valido = type(valor) in (bool, int) and valor in (0, 1)
                else:
                    valido = isinstance(valor, str) and bool(valor.strip())
                if not valido:
                    raise ValueError(f"{contexto}: valor inválido en {campo}")
            clave = fila[campos[0]]
            if clave in claves:
                raise ValueError(f"{contexto}: clave duplicada {clave}")
            claves.add(clave)
        datos[tabla] = filas
    sedes = {fila["id_sede"] for fila in datos["sedes"]}
    libros = {fila["isbn"] for fila in datos["libros"]}
    for fila in datos["ejemplares"]:
        if fila["id_sede"] not in sedes or fila["isbn"] not in libros:
            raise ValueError(f"Ejemplar {fila['codigo']}: sede o ISBN no incluido en los JSON")
    return datos


def importar_demo(ruta=RUTA_BASE_DATOS, carpeta=CARPETA_DEMO):
    datos = leer_datos(carpeta)
    for crear in (
        crear_tabla_sedes, crear_tabla_socios, crear_tablas_catalogo,
        crear_tabla_solicitudes, crear_tablas_remitos, crear_tabla_prestamos,
        crear_tablas_devoluciones, crear_tabla_reservas,
    ):
        crear(ruta)

    resumen = {}
    with closing(sqlite3.connect(ruta)) as conexion, conexion:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("BEGIN IMMEDIATE")
        for tabla in ("sedes", "socios", "libros"):
            campos = CAMPOS[tabla]
            agregados = 0
            for fila in datos[tabla]:
                existente = conexion.execute(
                    f"SELECT {', '.join(campos)} FROM {tabla} WHERE {campos[0]} = ?",
                    (fila[campos[0]],),
                ).fetchone()
                if existente is not None:
                    if tabla == "sedes" and existente[1] != fila["nombre"]:
                        raise ValueError(f"La sede {fila['id_sede']} ya existe con otro nombre")
                    continue
                conexion.execute(
                    f"INSERT INTO {tabla} ({', '.join(campos)}) "
                    f"VALUES ({', '.join('?' for _ in campos)})",
                    tuple(fila[campo] for campo in campos),
                )
                agregados += 1
            resumen[tabla] = agregados

        agregados = 0
        for fila in datos["ejemplares"]:
            id_libro = conexion.execute(
                "SELECT id_libro FROM libros WHERE isbn = ?", (fila["isbn"],)
            ).fetchone()[0]
            existente = conexion.execute(
                "SELECT id_libro, id_sede FROM ejemplares WHERE codigo = ?",
                (fila["codigo"],),
            ).fetchone()
            if existente is not None:
                if existente != (id_libro, fila["id_sede"]):
                    raise ValueError(f"El código {fila['codigo']} ya pertenece a otro libro o sede")
                continue
            conexion.execute(
                "INSERT INTO ejemplares (codigo, id_libro, id_sede, id_sede_actual, estado) "
                "VALUES (?, ?, ?, ?, 'Disponible')",
                (fila["codigo"], id_libro, fila["id_sede"], fila["id_sede"]),
            )
            agregados += 1
        resumen["ejemplares"] = agregados
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bd", type=Path, default=Path(RUTA_BASE_DATOS), help="Base SQLite de destino")
    parser.add_argument("--datos", type=Path, default=CARPETA_DEMO, help="Carpeta con los cuatro JSON")
    argumentos = parser.parse_args()
    try:
        resumen = importar_demo(argumentos.bd, argumentos.datos)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"No se pudo importar: {error}\n")
    print(f"Base: {argumentos.bd.resolve()}")
    for tabla, cantidad in resumen.items():
        print(f"{tabla}: {cantidad} agregados")
    print("Los registros existentes se conservaron sin cambios.")


if __name__ == "__main__":
    main()
