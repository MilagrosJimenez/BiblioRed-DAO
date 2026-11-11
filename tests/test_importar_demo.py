"""El importador se prueba únicamente contra bases temporales."""

import json
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from scripts.importar_demo import CARPETA_DEMO, importar_demo


class PruebasImportarDemo(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "demo.db"
        self.carpeta = Path(self.temporal.name) / "json"
        shutil.copytree(CARPETA_DEMO, self.carpeta)

    def modificar_json(self, nombre, modificar):
        archivo = self.carpeta / f"{nombre}.json"
        filas = json.loads(archivo.read_text(encoding="utf-8"))
        modificar(filas)
        archivo.write_text(json.dumps(filas), encoding="utf-8")

    def test_crea_base_completa_y_relaciones(self):
        resumen = importar_demo(self.ruta)
        self.assertEqual(resumen, dict(sedes=3, socios=8, libros=10, ejemplares=24))
        with closing(sqlite3.connect(self.ruta)) as db:
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM ejemplares e JOIN libros l "
                                        "ON l.id_libro = e.id_libro JOIN sedes s "
                                        "ON s.id_sede = e.id_sede "
                                        "WHERE e.estado = 'Disponible' "
                                        "AND e.id_sede_actual = e.id_sede").fetchone()[0], 24)
            for tabla in ("solicitudes_prestamo", "remitos", "prestamos", "devoluciones", "reservas"):
                self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0], 0)

    def test_reimportar_no_duplica_ni_reinicia_estados(self):
        importar_demo(self.ruta)
        with closing(sqlite3.connect(self.ruta)) as db, db:
            db.execute("UPDATE ejemplares SET estado = 'En revisión' WHERE codigo = 'DEMO-001-C'")
            db.execute("UPDATE socios SET habilitado = 0 WHERE documento = '99000001'")
        self.assertEqual(importar_demo(self.ruta), dict(sedes=0, socios=0, libros=0, ejemplares=0))
        with closing(sqlite3.connect(self.ruta)) as db:
            self.assertEqual(db.execute("SELECT estado FROM ejemplares WHERE codigo = 'DEMO-001-C'")
                             .fetchone()[0], "En revisión")
            self.assertEqual(db.execute("SELECT habilitado FROM socios WHERE documento = '99000001'")
                             .fetchone()[0], 0)

    def test_isbn_existente_se_reutiliza_sin_suponer_ids(self):
        importar_demo(self.ruta)
        with closing(sqlite3.connect(self.ruta)) as db, db:
            db.execute("INSERT INTO libros (isbn, titulo, autor, editorial) "
                       "VALUES ('OTRO', 'Libro local', 'Autor local', 'Editorial local')")
        self.modificar_json("ejemplares", lambda filas: filas.append(
            dict(codigo="DEMO-NUEVO", isbn="9780307474728", id_sede=901)))
        self.assertEqual(importar_demo(self.ruta, self.carpeta)["ejemplares"], 1)
        with closing(sqlite3.connect(self.ruta)) as db:
            self.assertEqual(db.execute("SELECT l.isbn FROM ejemplares e JOIN libros l "
                                        "ON l.id_libro = e.id_libro WHERE e.codigo = 'DEMO-NUEVO'")
                             .fetchone()[0], "9780307474728")
            self.assertEqual(db.execute("SELECT titulo FROM libros WHERE isbn = 'OTRO'")
                             .fetchone()[0], "Libro local")

    def test_referencia_invalida_no_crea_base(self):
        self.modificar_json("ejemplares", lambda filas: filas[0].update(isbn="NO-EXISTE"))
        with self.assertRaisesRegex(ValueError, "sede o ISBN"):
            importar_demo(self.ruta, self.carpeta)
        self.assertFalse(self.ruta.exists())

    def test_clave_duplicada_se_rechaza(self):
        self.modificar_json("socios", lambda filas: filas.append(filas[0].copy()))
        with self.assertRaisesRegex(ValueError, "clave duplicada"):
            importar_demo(self.ruta, self.carpeta)

    def test_conflicto_revierte_toda_la_carga(self):
        importar_demo(self.ruta)
        self.modificar_json("socios", lambda filas: filas.append(dict(
            documento="99000099", nombre="Nuevo", apellido="Demo", telefono="0",
            correo="nuevo@example.invalid", habilitado=True)))
        self.modificar_json("ejemplares", lambda filas: filas[-1].update(id_sede=902))
        with self.assertRaisesRegex(ValueError, "otro libro o sede"):
            importar_demo(self.ruta, self.carpeta)
        with closing(sqlite3.connect(self.ruta)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM socios WHERE documento = '99000099'")
                             .fetchone()[0], 0)

    def test_sede_con_otro_nombre_no_se_reutiliza(self):
        importar_demo(self.ruta)
        self.modificar_json("sedes", lambda filas: filas[0].update(nombre="Otra sede"))
        with self.assertRaisesRegex(ValueError, "otro nombre"):
            importar_demo(self.ruta, self.carpeta)


if __name__ == "__main__":
    unittest.main()
