
import sqlite3

from datos.base_datos import RUTA_BASE_DATOS


def crear_tablas_catalogo():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT NOT NULL UNIQUE,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            editorial TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ejemplares (
            id_ejemplar INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            id_libro INTEGER NOT NULL,
            id_sede INTEGER NOT NULL,
            id_sede_actual INTEGER,
            estado TEXT NOT NULL,
            FOREIGN KEY (id_libro) REFERENCES libros(id_libro),
            FOREIGN KEY (id_sede) REFERENCES sedes(id_sede)
        )
    """)

    conexion.commit()
    conexion.close()


def guardar_libro(libro):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id_libro FROM libros WHERE isbn = ?",
        (libro.isbn,)
    )

    if cursor.fetchone() is not None:
        conexion.close()
        return False

    cursor.execute("""
        INSERT INTO libros (isbn, titulo, autor, editorial)
        VALUES (?, ?, ?, ?)
    """, (
        libro.isbn,
        libro.titulo,
        libro.autor,
        libro.editorial
    ))

    conexion.commit()
    conexion.close()

    return True


def consultar_libros():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT l.id_libro, l.isbn, l.titulo, l.autor, l.editorial,
               COUNT(e.id_ejemplar),
               SUM(
                   CASE WHEN e.estado = 'Disponible'
                   THEN 1 ELSE 0 END
               )
        FROM libros l
        LEFT JOIN ejemplares e ON e.id_libro = l.id_libro
        GROUP BY l.id_libro, l.isbn, l.titulo, l.autor, l.editorial
        ORDER BY l.titulo
    """)

    libros = cursor.fetchall()
    conexion.close()

    return libros


def actualizar_libro(libro):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE libros
        SET titulo = ?, autor = ?, editorial = ?
        WHERE id_libro = ?
    """, (
        libro.titulo,
        libro.autor,
        libro.editorial,
        libro.id_libro
    ))

    conexion.commit()
    conexion.close()


def guardar_ejemplar(ejemplar):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id_ejemplar FROM ejemplares WHERE codigo = ?",
        (ejemplar.codigo,)
    )

    if cursor.fetchone() is not None:
        conexion.close()
        return False

    cursor.execute("""
        INSERT INTO ejemplares
            (codigo, id_libro, id_sede, id_sede_actual, estado)
        VALUES (?, ?, ?, ?, ?)
    """, (
        ejemplar.codigo,
        ejemplar.id_libro,
        ejemplar.id_sede,
        ejemplar.id_sede,
        ejemplar.estado
    ))

    conexion.commit()
    conexion.close()

    return True


def consultar_ejemplares():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT e.id_ejemplar, e.codigo, l.titulo, l.isbn,
               s.nombre, e.estado, e.id_libro, e.id_sede,
               COALESCE(actual.nombre, s.nombre) AS ubicacion_actual
        FROM ejemplares e
        JOIN libros l ON e.id_libro = l.id_libro
        JOIN sedes s ON e.id_sede = s.id_sede
        LEFT JOIN sedes actual
               ON actual.id_sede = COALESCE(e.id_sede_actual, e.id_sede)
        ORDER BY e.id_ejemplar
    """)

    ejemplares = cursor.fetchall()
    conexion.close()

    return ejemplares
