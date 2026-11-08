"""Pruebas de filtros y controles de diseño; no abren ventanas ni usan DB."""
import unittest
import flet as ft

from interfaces.ui_moderno import (
    normalizar, modernizar, texto_visible, buscador_de_tabla,
    buscador_de_tarjetas
)


class PaginaFalsa:
    def __init__(self):
        self.actualizaciones = 0

    def update(self):
        self.actualizaciones += 1


class PruebasBuscadores(unittest.TestCase):
    def test_normalizacion(self):
        self.assertEqual(normalizar("JIMÉNEZ"), "jimenez")
        self.assertEqual(normalizar("  María  "), "maria")

    def test_buscadores_contextuales(self):
        from interfaces.ui_moderno import sugerencia_de_busqueda
        sedes = sugerencia_de_busqueda(["Sedes registradas"])
        socios = sugerencia_de_busqueda(["Socios registrados"])
        catalogo = sugerencia_de_busqueda(["Catálogo de libros"])
        self.assertIn("ID", sedes)
        self.assertIn("dirección", sedes)
        self.assertNotIn("DNI", sedes)
        self.assertIn("documento", socios)
        self.assertIn("ISBN", catalogo)

    def test_busqueda_de_sedes_muestra_sugerencia_propia(self):
        pagina = PaginaFalsa()
        tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("ID"))],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("9001"))])]
        )
        panel = ft.Column([
            ft.Text("Sedes registradas"),
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
        ])
        modernizar(panel, pagina)
        campo = next(
            c for x in panel.controls if isinstance(x, ft.Row)
            for c in x.controls if isinstance(c, ft.TextField)
        )
        self.assertIn("dirección", campo.hint_text)
        self.assertNotIn("DNI", campo.hint_text)
        campo.value = "9"
        campo.on_submit(None)
        self.assertEqual(len(tabla.rows), 1)

    def test_filtra_tabla_por_una_letra_y_numero(self):
        pagina = PaginaFalsa()
        tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Socio")),
                     ft.DataColumn(ft.Text("DNI"))],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Jiménez")), ft.DataCell(ft.Text("1001"))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Ana")), ft.DataCell(ft.Text("2450"))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Jorge")), ft.DataCell(ft.Text("765"))
                ])
            ]
        )
        panel = ft.Column([
            ft.Text("Socios registrados"),
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
        ])
        modernizar(panel, pagina)
        campos = [
            c for x in panel.controls if isinstance(x, ft.Row)
            for c in x.controls if isinstance(c, ft.TextField)
        ]
        self.assertEqual(len(campos), 1)
        campo = campos[0]
        campo.value = "j"
        campo.on_change(None)
        self.assertEqual(len(tabla.rows), 2)
        campo.value = "1"
        campo.on_submit(None)
        self.assertEqual(len(tabla.rows), 1)
        campo.value = "MARÍA"
        campo.on_change(None)
        self.assertEqual(len(tabla.rows), 0)
        campo.value = ""
        campo.on_change(None)
        self.assertEqual(len(tabla.rows), 3)

    def test_filtra_tarjetas_de_remitos(self):
        pagina = PaginaFalsa()
        tarjetas = ft.Column([
            ft.Container(content=ft.Text("Remito 1 - Libro A")),
            ft.Container(content=ft.Text("Remito 20 - Libro B"))
        ])
        panel = ft.Column([ft.Text("Remitos registrados"), tarjetas])
        modernizar(panel, pagina)
        campo = next(
            c for x in panel.controls if isinstance(x, ft.Row)
            for c in x.controls if isinstance(c, ft.TextField)
        )
        campo.value = "20"
        campo.on_change(None)
        self.assertEqual(len(tarjetas.controls), 1)
        self.assertIn("20", texto_visible(tarjetas.controls[0]))
        campo.value = ""
        campo.on_submit(None)
        self.assertEqual(len(tarjetas.controls), 2)

    def test_estructura_navegacion_moderna(self):
        from types import SimpleNamespace
        from interfaces.ventana_completa import VentanaCompleta

        class Pagina:
            def __init__(self):
                self.window = SimpleNamespace(width=0, height=0)
                self.controls = []

            def add(self, control):
                self.controls.append(control)

            def update(self):
                pass

        ventana = VentanaCompleta.__new__(VentanaCompleta)
        ventana._page = Pagina()
        ventana._contenido = ft.Column([])
        ventana._crear_estructura()
        self.assertEqual(len(ventana._nav_items), 12)
        self.assertEqual(ventana._pagina_activa, "Inicio")
        self.assertEqual(len(ventana._page.controls), 1)

    def test_dashboard_sin_expand_en_filas_ajustables(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from interfaces.ventana_completa import VentanaCompleta

        class Pagina:
            def __init__(self):
                self.window = SimpleNamespace(width=0, height=0)
                self.controls = []

            def add(self, control):
                self.controls.append(control)

            def update(self):
                pass

        app = VentanaCompleta.__new__(VentanaCompleta)
        app._page = Pagina()
        app._contenido = ft.Column([])
        app._crear_estructura()
        with patch(
            "interfaces.ventana_completa.consultar_sedes", return_value=[]
        ), patch(
            "interfaces.ventana_completa.consultar_socios", return_value=[]
        ), patch(
            "interfaces.ventana_completa.consultar_prestamos", return_value=[]
        ), patch(
            "interfaces.ventana_completa.consultar_reservas", return_value=[]
        ):
            app._mostrar_inicio()

        filas = []
        def visitar(control):
            if isinstance(control, ft.Row):
                filas.append(control)
            if isinstance(control, (ft.Row, ft.Column)):
                for hijo in control.controls:
                    visitar(hijo)
            if isinstance(control, ft.Container) and control.content:
                visitar(control.content)

        visitar(app._contenido)
        ajustables = [fila for fila in filas if fila.wrap]
        for fila in ajustables:
            for control in fila.controls:
                self.assertFalse(
                    getattr(control, "expand", False),
                    "Una fila con wrap no puede contener tarjetas expandibles"
                )
        filas_cuatro = [
            fila for fila in filas
            if len(fila.controls) == 4
            and all(isinstance(c, ft.Container) for c in fila.controls)
        ]
        self.assertGreaterEqual(len(filas_cuatro), 2)
        self.assertTrue(all(
            not fila.wrap for fila in filas_cuatro
        ))

    def test_button_y_controles_modernos(self):
        panel = ft.Column([
            ft.Container(
                bgcolor="white",
                content=ft.Column([
                    ft.TextField(label="Nombre"),
                    ft.Button("Guardar", bgcolor="#63BDEB")
                ])
            )
        ])
        modernizar(panel, PaginaFalsa())
        self.assertEqual(panel.controls[0].border_radius, 15)


class PruebaRangoSemanalSedes(unittest.TestCase):
    def test_viernes_a_lunes_es_valido_y_se_guarda(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from interfaces.ventana_flet import VentanaFlet

        vista = VentanaFlet.__new__(VentanaFlet)
        vista._editando_id = None
        vista._campo_id = SimpleNamespace(value="9002")
        vista._campo_nombre = SimpleNamespace(value="Biblioteca Horario")
        vista._campo_direccion = SimpleNamespace(value="Calle 10")
        vista._campo_telefono = SimpleNamespace(value="3512222")
        vista._dia_desde = SimpleNamespace(value="Viernes")
        vista._dia_hasta = SimpleNamespace(value="Lunes")
        vista._hora_desde = SimpleNamespace(value="09:00")
        vista._hora_hasta = SimpleNamespace(value="18:00")
        vista._atencion_24h = SimpleNamespace(value=False)
        vista._horario_anterior = ""
        vista._dias = [
            "Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"
        ]
        mensajes = []
        vista._mostrar_mensaje = lambda titulo, texto: mensajes.append((titulo, texto))
        vista._mostrar_sedes = lambda: None

        with patch("interfaces.ventana_flet.guardar_sede", return_value=True) as guardar:
            vista._guardar_sede(None)
        self.assertEqual(guardar.call_count, 1)
        self.assertEqual(guardar.call_args.args[0].horarios,
                         "Viernes a lunes de 09:00 a 18:00")
        self.assertEqual(mensajes[-1][0], "Operación realizada")

    @staticmethod
    def _crear_vista(hora_desde, hora_hasta, atencion_24h=False):
        from types import SimpleNamespace
        from interfaces.ventana_flet import VentanaFlet

        vista = VentanaFlet.__new__(VentanaFlet)
        vista._editando_id = None
        vista._horario_anterior = ""
        vista._campo_id = SimpleNamespace(value="9003")
        vista._campo_nombre = SimpleNamespace(value="Biblioteca Horario")
        vista._campo_direccion = SimpleNamespace(value="Calle 10")
        vista._campo_telefono = SimpleNamespace(value="3512222")
        vista._dia_desde = SimpleNamespace(value="Viernes")
        vista._dia_hasta = SimpleNamespace(value="Lunes")
        vista._hora_desde = SimpleNamespace(value=hora_desde, disabled=atencion_24h)
        vista._hora_hasta = SimpleNamespace(value=hora_hasta, disabled=atencion_24h)
        vista._atencion_24h = SimpleNamespace(value=atencion_24h)
        vista._vista_previa = SimpleNamespace(value="")
        vista._dias = [
            "Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"
        ]
        vista._mostrar_sedes = lambda: None
        return vista

    def test_turno_nocturno_aceptado_con_dia_siguiente(self):
        from unittest.mock import patch
        vista = self._crear_vista("18:00", "09:00")
        mensajes = []
        vista._mostrar_mensaje = lambda titulo, texto: mensajes.append(titulo)

        with patch("interfaces.ventana_flet.guardar_sede", return_value=True) as guardar:
            vista._guardar_sede(None)
        guardar.assert_called_once()
        self.assertEqual(
            guardar.call_args.args[0].horarios,
            "Viernes a lunes de 18:00 a 09:00 (día siguiente)"
        )
        self.assertEqual(mensajes[-1], "Operación realizada")

    def test_horas_iguales_se_rechazan_sin_24_horas(self):
        from unittest.mock import patch
        vista = self._crear_vista("09:00", "09:00")
        mensajes = []
        vista._mostrar_mensaje = lambda titulo, texto: mensajes.append(titulo)
        with patch("interfaces.ventana_flet.guardar_sede") as guardar:
            vista._guardar_sede(None)
        guardar.assert_not_called()
        self.assertEqual(mensajes[-1], "Horario inválido")

    def test_atencion_24_horas_sin_seleccionar_horas(self):
        from unittest.mock import patch
        vista = self._crear_vista(None, None, atencion_24h=True)
        mensajes = []
        vista._mostrar_mensaje = lambda titulo, texto: mensajes.append(titulo)
        with patch("interfaces.ventana_flet.guardar_sede", return_value=True) as guardar:
            vista._guardar_sede(None)
        self.assertEqual(
            guardar.call_args.args[0].horarios,
            "Viernes a lunes: atención 24 horas"
        )
        self.assertEqual(mensajes[-1], "Operación realizada")

    def test_atencion_24_horas_requiere_dias(self):
        from unittest.mock import patch
        vista = self._crear_vista(None, None, atencion_24h=True)
        vista._dia_desde.value = None
        mensajes = []
        vista._mostrar_mensaje = lambda titulo, texto: mensajes.append(titulo)
        with patch("interfaces.ventana_flet.guardar_sede") as guardar:
            vista._guardar_sede(None)
        guardar.assert_not_called()
        self.assertEqual(mensajes[-1], "Horarios incompletos")

    def test_alternar_24_horas_bloquea_y_habilita_selectores(self):
        vista = self._crear_vista("18:00", "09:00", atencion_24h=True)
        vista._page = PaginaFalsa()
        vista._cambiar_atencion_24h()
        self.assertTrue(vista._hora_desde.disabled)
        self.assertTrue(vista._hora_hasta.disabled)
        self.assertIn("atención 24 horas", vista._vista_previa.value)
        vista._atencion_24h.value = False
        vista._cambiar_atencion_24h()
        self.assertFalse(vista._hora_desde.disabled)
        self.assertFalse(vista._hora_hasta.disabled)
        self.assertIn("día siguiente", vista._vista_previa.value)

    def test_edicion_sin_cambios_conserva_horario_original(self):
        from unittest.mock import patch
        vista = self._crear_vista(None, None)
        vista._editando_id = 9003
        vista._horario_anterior = "Lunes a viernes de 09:00 a 18:00"
        vista._dia_desde.value = None
        vista._dia_hasta.value = None
        mensajes = []
        vista._mostrar_mensaje = lambda titulo, texto: mensajes.append(titulo)
        with patch("interfaces.ventana_flet.actualizar_datos_sede") as actualizar:
            vista._guardar_sede(None)
        actualizar.assert_called_once()
        self.assertEqual(
            actualizar.call_args.args[0].horarios,
            "Lunes a viernes de 09:00 a 18:00"
        )
        self.assertEqual(mensajes[-1], "Operación realizada")


class PruebasIconosAcciones(unittest.TestCase):
    def test_ayudas_y_tamanos_uniformes(self):
        from interfaces.ui_moderno import icono_accion

        for tipo in (
            "ver", "editar", "habilitar", "inhabilitar",
            "cancelar", "historial", "despachar", "recibir", "atender"
        ):
            boton = icono_accion(tipo, "Acción de prueba", lambda e: None)
            self.assertIsInstance(boton, ft.IconButton)
            self.assertEqual(boton.tooltip, "Acción de prueba")
            self.assertEqual(boton.width, 38)
            self.assertEqual(boton.height, 38)
            self.assertEqual(boton.icon_size, 19)
            self.assertIsNotNone(boton.on_click)

        with self.assertRaises(ValueError):
            icono_accion("desconocida", "No existe", lambda e: None)

    def test_socios_iconos_conservan_acciones(self):
        from interfaces.ventana_socios import VentanaSocios

        pantalla = VentanaSocios.__new__(VentanaSocios)
        llamadas = []
        pantalla._ver = lambda datos: llamadas.append(("ver", datos[1]))
        pantalla._cargar_edicion = lambda datos: llamadas.append(("editar", datos[1]))
        pantalla._cambiar_estado = lambda datos: llamadas.append(("estado", datos[1]))

        for habilitado, etiqueta in ((1, "Inhabilitar socio"),
                                     (0, "Habilitar socio")):
            datos = (1, "99001234", "Lucía", "Prueba", "351", None, habilitado)
            fila = pantalla._crear_fila(datos)
            acciones = fila.cells[-1].content.controls
            self.assertEqual(len(acciones), 3)
            self.assertTrue(all(isinstance(a, ft.IconButton) for a in acciones))
            self.assertEqual(acciones[0].tooltip, "Ver detalles del socio")
            self.assertEqual(acciones[1].tooltip, "Editar socio")
            self.assertEqual(acciones[2].tooltip, etiqueta)
            for boton in acciones:
                boton.on_click(None)

        self.assertEqual(
            llamadas,
            [("ver", "99001234"), ("editar", "99001234"), ("estado", "99001234")] * 2
        )


class PruebaNavegacionCompleta(unittest.TestCase):
    def test_todas_las_pantallas_abren_con_base_temporal(self):
        import os
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import patch
        from datos import (
            base_datos, catalogo_datos, prestamos_datos, remitos_datos,
            prestamos_efectivos_datos, devoluciones_datos, reservas_datos,
            consultas_bibliored_datos
        )
        from interfaces.ventana_completa import VentanaCompleta

        class PaginaFalsa:
            def __init__(self):
                self.window = SimpleNamespace(width=0, height=0)
                self.controls = []

            def add(self, control):
                self.controls.append(control)

            def update(self):
                pass

            def show_dialog(self, dialogo):
                pass

            def pop_dialog(self):
                pass

        archivo = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        archivo.close()
        ruta = archivo.name
        parches = [
            patch.object(mod, "RUTA_BASE_DATOS", ruta)
            for mod in (
                base_datos, catalogo_datos, prestamos_datos, remitos_datos,
                prestamos_efectivos_datos, devoluciones_datos,
                reservas_datos, consultas_bibliored_datos,
            )
        ]
        try:
            for p in parches:
                p.start()
            base_datos.crear_tabla_sedes()
            base_datos.crear_tabla_socios()
            catalogo_datos.crear_tablas_catalogo()
            prestamos_datos.crear_tabla_solicitudes()
            remitos_datos.crear_tablas_remitos()
            prestamos_efectivos_datos.crear_tabla_prestamos()
            devoluciones_datos.crear_tablas_devoluciones()
            reservas_datos.crear_tabla_reservas()

            app = VentanaCompleta(PaginaFalsa())
            for nombre in (
                "_mostrar_sedes", "_mostrar_socios", "_mostrar_catalogo",
                "_mostrar_solicitudes", "_mostrar_remitos",
                "_mostrar_prestamos", "_mostrar_devoluciones",
                "_mostrar_reservas", "_mostrar_inventario",
                "_mostrar_historial_lecturas", "_mostrar_reportes",
                "_mostrar_inicio"
            ):
                with self.subTest(pantalla=nombre):
                    getattr(app, nombre)()
                    if nombre == "_mostrar_sedes":
                        self.assertEqual(app._campo_id.label, "ID")
                        self.assertEqual(app._campo_id.width, 185)
                        self.assertEqual(app._campo_telefono.width, 325)
                        self.assertEqual(app._dia_desde.label, "Desde")
                        self.assertEqual(app._dia_hasta.label, "Hasta")
                        self.assertEqual(app._hora_desde.label, "Desde")
                        self.assertEqual(app._hora_hasta.label, "Hasta")

            # La nueva navegación separa formulario y consulta, sin duplicarlos.
            app._mostrar_sedes()
            self.assertEqual(len(app._modulo_zona.controls), 1)
            self.assertIs(app._modulo_zona.controls[0].controls[0],
                          app._modulo_listado)
            app._cambiar_modo("Administrar sedes", "registrar")
            self.assertIs(app._modulo_zona.controls[0].controls[0],
                          app._modulo_formulario)
            app._mostrar_socios()
            app._cambiar_modo("Administrar socios", "consultar")
            self.assertIs(app._modulo_zona.controls[0].controls[0],
                          app._modulo_listado)
            app._mostrar_solicitudes()
            app._cambiar_modo("Solicitudes de préstamo", "registrar")
            self.assertIs(app._modulo_zona.controls[0].controls[0],
                          app._modulo_formulario)
            app._mostrar_remitos()
            self.assertIs(app._modulo_zona.controls[0].controls[0],
                          app._modulo_listado)
            app._mostrar_inicio()
            self.assertIsNone(app._contenido.scroll)
            self.assertEqual(app._buscador_general.label,
                             "Buscar en todo BiblioRed")

            # Buscar al escribir y pulsar un resultado lleva a consultar
            # el módulo correcto sin crear otra ventana.
            from unittest.mock import patch as _patch_busqueda
            resultado = {
                "tipo": "Sede",
                "titulo": "Biblioteca Prueba",
                "detalle": "ID 9001",
                "destino": "Administrar sedes"
            }
            with _patch_busqueda(
                "interfaces.ventana_completa.buscar_en_bibliored",
                return_value=[resultado]
            ):
                app._buscador_general.value = "9001"
                app._buscador_general.on_change(None)
            self.assertTrue(app._panel_resultados.visible)
            self.assertFalse(app._panel_accesos.visible)
            self.assertEqual(len(app._resultados_global.controls), 1)
            app._abrir_resultado(resultado)
            self.assertEqual(app._pagina_activa, "Administrar sedes")
            self.assertEqual(app._modos["Administrar sedes"], "consultar")
            filtro = app._encontrar_buscador(app._contenido)
            self.assertIsNotNone(filtro)
            self.assertEqual(filtro.value, "9001")

            # También se prueban las pantallas secundarias que se reconstruyen.
            from interfaces.ventana_catalogo import VentanaCatalogo
            from interfaces.ventana_devoluciones import VentanaDevoluciones
            from interfaces.ventana_reservas import VentanaReservas
            catalogo = VentanaCatalogo(app._page)
            catalogo.crear_contenido()
            self.assertEqual(catalogo._modo, "consultar")
            self.assertIs(catalogo._zona.controls[0].controls[0],
                          catalogo._listado)
            catalogo._cambiar_modo("registrar")
            self.assertIs(catalogo._zona.controls[0].controls[0],
                          catalogo._formulario)
            catalogo._cambiar_seccion("ejemplares")
            self.assertEqual(catalogo._modo, "consultar")
            devoluciones = VentanaDevoluciones(app._page)
            devoluciones.crear_contenido()
            devoluciones._cambiar("retornos")
            reservas = VentanaReservas(app._page)
            reservas.crear_contenido()
            reservas._cambiar("reservas")
        finally:
            for p in reversed(parches):
                p.stop()
            os.unlink(ruta)

    
class PruebasListadosCompactos(unittest.TestCase):
    def test_catalogo_muestra_datos_y_acciones_sin_tabla_ancha(self):
        from unittest.mock import patch
        from interfaces.ventana_catalogo import VentanaCatalogo

        pagina = PaginaFalsa()
        with patch(
            "interfaces.ventana_catalogo.CatalogoServicio.listar_libros",
            return_value=[(1, "ISBN01", "Libro de prueba", "Autora", "Editorial", 1, 1)]
        ):
            vista = VentanaCatalogo(pagina)
            vista.crear_contenido()
        contenido = vista._zona
        encontrados = []

        def recorrer(control):
            encontrados.append(control)
            if isinstance(control, (ft.Column, ft.Row)):
                for hijo in control.controls:
                    recorrer(hijo)
            elif isinstance(control, ft.Container):
                recorrer(control.content)

        recorrer(contenido)
        self.assertFalse(any(isinstance(x, ft.DataTable) for x in encontrados))
        textos = " ".join(
            x.value or "" for x in encontrados if isinstance(x, ft.Text)
        )
        self.assertIn("Libro de prueba", textos)
        botones = [
            x for x in encontrados if isinstance(x, ft.IconButton)
        ]
        self.assertTrue(any(x.tooltip == "Editar libro" for x in botones))
        self.assertTrue(any(x.tooltip == "Ver detalles del libro" for x in botones))

    def test_solicitudes_muestran_estado_y_cancelacion(self):
        from unittest.mock import patch
        from interfaces.ventana_solicitudes import VentanaSolicitudes
        pagina = PaginaFalsa()
        solicitud = (1, "Ana, Prueba", None, "EJ-1", None,
                     "Sede Centro", "Sede Norte", "Interbibliotecario",
                     "Pendiente de traslado")
        with patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_socios_habilitados",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_sedes_activas",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_ejemplares_disponibles",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_solicitudes",
            return_value=[solicitud]
        ):
            pantalla = VentanaSolicitudes(pagina, lambda: None)
            pantalla.crear_contenido()
        lista = pantalla.crear_contenido() if False else None
        # Comprobar estructura directamente desde la vista reconstruida.
        with patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_socios_habilitados",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_sedes_activas",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_ejemplares_disponibles",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_solicitudes",
            return_value=[solicitud]
        ):
            contenido = pantalla.crear_contenido()
        encontrados = []

        def recorrer(control):
            encontrados.append(control)
            if isinstance(control, (ft.Column, ft.Row)):
                for hijo in control.controls:
                    recorrer(hijo)
            elif isinstance(control, ft.Container):
                recorrer(control.content)

        recorrer(contenido)
        self.assertFalse(any(isinstance(x, ft.DataTable) for x in encontrados))
        textos = " ".join(
            x.value or "" for x in encontrados if isinstance(x, ft.Text)
        )
        self.assertIn("Pendiente de traslado", textos)
        self.assertIn("Sede Norte", textos)
        self.assertTrue(any(
            isinstance(x, ft.IconButton) and x.tooltip == "Cancelar solicitud"
            for x in encontrados
        ))

    def test_tarjetas_sin_expand_en_filas_wrap(self):
        """Previene el layout gris en las tarjetas de libros y solicitudes."""
        from unittest.mock import patch
        from interfaces.ventana_catalogo import VentanaCatalogo
        from interfaces.ventana_solicitudes import VentanaSolicitudes

        with patch(
            "interfaces.ventana_catalogo.CatalogoServicio.listar_libros",
            return_value=[
                (1, "ISBN01", "Libro de prueba", "Autor", "Editorial", 1, 1)
            ]
        ):
            catalogo = VentanaCatalogo(PaginaFalsa())
            catalogo.crear_contenido()

        solicitud = (
            1, "Prueba, Ana", None, "EJ-1", None,
            "Centro", "Norte", "Interbibliotecario", "Pendiente"
        )
        with patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_socios_habilitados",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_sedes_activas",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_ejemplares_disponibles",
            return_value=[]
        ), patch(
            "interfaces.ventana_solicitudes.PrestamosServicio.listar_solicitudes",
            return_value=[solicitud]
        ):
            solicitudes = VentanaSolicitudes(PaginaFalsa(), lambda: None)
            contenido_solicitudes = solicitudes.crear_contenido()

        def recorrer(control):
            if isinstance(control, ft.Row) and control.wrap:
                for hijo in control.controls:
                    self.assertFalse(
                        getattr(hijo, "expand", False),
                        "No usar expand=True en filas con wrap"
                    )
            if isinstance(control, (ft.Row, ft.Column)):
                for hijo in control.controls:
                    recorrer(hijo)
            elif isinstance(control, ft.Container):
                recorrer(control.content)

        recorrer(catalogo._zona)
        recorrer(contenido_solicitudes)


if __name__ == "__main__":
    unittest.main()
