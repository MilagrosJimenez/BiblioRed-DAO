
import os
import tkinter as tk
from tkinter import ttk, messagebox

from clases.sede import Sede
from datos.base_datos import (
    crear_tabla_sedes,
    guardar_sede,
    consultar_sedes,
    actualizar_estado_sede
)


class VentanaPrincipal:

    def __init__(self):
        crear_tabla_sedes()

        self._ventana = tk.Tk()
        self._ventana.title("BiblioRed | UTN Facultad Regional Córdoba")
        self._ventana.geometry("1120x720")
        self._ventana.minsize(1000, 620)
        self._ventana.configure(bg="#F2F8FC")

        self._azul = "#123D65"
        self._fondo = "#F2F8FC"
        self._texto = "#183B56"

        self._crear_estilo_tabla()
        self._crear_estructura()
        self._mostrar_inicio()

    def _crear_estilo_tabla(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Sedes.Treeview",
            background="white",
            fieldbackground="white",
            foreground=self._texto,
            font=("Segoe UI", 10),
            rowheight=32
        )

        estilo.configure(
            "Sedes.Treeview.Heading",
            background="#E4F2FC",
            foreground=self._azul,
            font=("Segoe UI", 10, "bold")
        )

        estilo.map(
            "Sedes.Treeview",
            background=[("selected", "#BCE7FF")],
            foreground=[("selected", self._texto)]
        )

    def _crear_estructura(self):
        # ENCABEZADO
        encabezado = tk.Frame(
            self._ventana,
            bg="white",
            height=110
        )
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        encabezado_texto = tk.Frame(
            encabezado,
            bg="white"
        )
        encabezado_texto.pack(
            side="left",
            padx=38,
            pady=20
        )

        tk.Label(
            encabezado_texto,
            text="BiblioRed",
            bg="white",
            fg=self._azul,
            font=("Segoe UI", 26, "bold")
        ).pack(anchor="w")

        tk.Label(
            encabezado_texto,
            text="Sistema de préstamos interbibliotecarios",
            bg="white",
            fg="#58758D",
            font=("Segoe UI", 11)
        ).pack(anchor="w")

        # LOGO UTN
        ruta_logo = os.path.join(
            os.path.dirname(__file__),
            "..",
            "imagenes",
            "logo_utn.png"
        )

        try:
            self._logo_original = tk.PhotoImage(file=ruta_logo)
            self._logo = self._logo_original.subsample(4, 4)

            tk.Label(
                encabezado,
                image=self._logo,
                bg="white"
            ).pack(side="right", padx=30)

        except (tk.TclError, FileNotFoundError):
            tk.Label(
                encabezado,
                text="UTN FRC",
                bg="white",
                fg="#1736B3",
                font=("Segoe UI", 18, "bold")
            ).pack(side="right", padx=30)

        # CUERPO PRINCIPAL
        cuerpo = tk.Frame(
            self._ventana,
            bg=self._fondo
        )
        cuerpo.pack(fill="both", expand=True)

        # MENÚ LATERAL
        menu = tk.Frame(
            cuerpo,
            bg=self._azul,
            width=230
        )
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        tk.Label(
            menu,
            text="NAVEGACIÓN",
            bg=self._azul,
            fg="#B6D8EE",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=25, pady=(26, 14))

        self._boton_inicio = self._crear_boton_menu(
            menu,
            "Inicio",
            self._mostrar_inicio
        )

        self._boton_sedes = self._crear_boton_menu(
            menu,
            "Administrar sedes",
            self._mostrar_sedes
        )

        tk.Label(
            menu,
            text="PRÓXIMAMENTE",
            bg=self._azul,
            fg="#B6D8EE",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=25, pady=(30, 10))

        for nombre in (
            "Socios",
            "Catálogo y ejemplares",
            "Préstamos y reservas",
            "Envíos y devoluciones",
            "Reportes"
        ):
            tk.Label(
                menu,
                text="  " + nombre,
                bg=self._azul,
                fg="#C2D5E3",
                anchor="w",
                font=("Segoe UI", 10),
                pady=9
            ).pack(fill="x", padx=20)

        tk.Label(
            menu,
            text="DAO 2026 - UTN FRC",
            bg=self._azul,
            fg="#A9C6DA",
            font=("Segoe UI", 9)
        ).pack(side="bottom", pady=20)

        # CONTENIDO
        self._contenido = tk.Frame(
            cuerpo,
            bg=self._fondo
        )
        self._contenido.pack(
            side="left",
            fill="both",
            expand=True,
            padx=28,
            pady=20
        )

    def _crear_boton_menu(self, padre, texto, accion):
        boton = tk.Button(
            padre,
            text="  " + texto,
            command=accion,
            bg=self._azul,
            fg="white",
            anchor="w",
            font=("Segoe UI", 12),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=12,
            cursor="hand2"
        )

        boton.pack(fill="x", padx=12, pady=4)

        return boton

    def _seleccionar_menu(self, seccion):
        for nombre, boton in (
            ("inicio", self._boton_inicio),
            ("sedes", self._boton_sedes)
        ):
            if nombre == seccion:
                boton.configure(
                    bg="#BCE7FF",
                    fg=self._azul
                )
            else:
                boton.configure(
                    bg=self._azul,
                    fg="white"
                )

    def _limpiar_contenido(self):
        for elemento in self._contenido.winfo_children():
            elemento.destroy()

    def _crear_titulo(self, titulo, descripcion):
        tk.Label(
            self._contenido,
            text=titulo,
            bg=self._fondo,
            fg=self._azul,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")

        tk.Label(
            self._contenido,
            text=descripcion,
            bg=self._fondo,
            fg="#678197",
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(3, 16))

    def _crear_tarjeta(self, padre, titulo, numero, descripcion):
        tarjeta = tk.Frame(
            padre,
            bg="white",
            highlightbackground="#D9EAF4",
            highlightthickness=1
        )

        tarjeta.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            tarjeta,
            text=titulo,
            bg="white",
            fg="#678197",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(18, 7))

        tk.Label(
            tarjeta,
            text=str(numero),
            bg="white",
            fg=self._azul,
            font=("Segoe UI", 27, "bold")
        ).pack(anchor="w", padx=20)

        tk.Label(
            tarjeta,
            text=descripcion,
            bg="white",
            fg="#7891A4",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=20, pady=(4, 17))

    def _mostrar_inicio(self):
        self._seleccionar_menu("inicio")
        self._limpiar_contenido()

        self._crear_titulo(
            "Panel principal",
            "Bienvenida al sistema de gestión de bibliotecas"
        )

        sedes = consultar_sedes()
        activas = 0

        for sede in sedes:
            if sede[5] == 1:
                activas += 1

        tarjetas = tk.Frame(
            self._contenido,
            bg=self._fondo
        )
        tarjetas.pack(fill="x")

        self._crear_tarjeta(
            tarjetas,
            "Sedes registradas",
            len(sedes),
            "Total de bibliotecas"
        )

        self._crear_tarjeta(
            tarjetas,
            "Sedes activas",
            activas,
            "Habilitadas para operar"
        )

        bienvenida = tk.Frame(
            self._contenido,
            bg="white",
            highlightbackground="#D9EAF4",
            highlightthickness=1
        )
        bienvenida.pack(fill="x", pady=28)

        tk.Label(
            bienvenida,
            text="Empezá administrando las sedes",
            bg="white",
            fg=self._azul,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=24, pady=(24, 10))

        tk.Label(
            bienvenida,
            text="Registrá las bibliotecas de la red y consultá sus datos.\n"
                 "Después incorporaremos socios, libros, préstamos y traslados.",
            bg="white",
            fg="#59758B",
            justify="left",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=24)

        tk.Button(
            bienvenida,
            text="Administrar sedes",
            command=self._mostrar_sedes,
            bg="#62BDEC",
            fg="#083756",
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=12,
            cursor="hand2"
        ).pack(anchor="w", padx=24, pady=24)

    def _crear_campo(self, padre, texto):
        tk.Label(
            padre,
            text=texto,
            bg="white",
            fg=self._texto,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(5, 2))

        campo = tk.Entry(
            padre,
            bg="#F6FBFF",
            fg=self._texto,
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 11)
        )
        campo.pack(fill="x", ipady=5)

        return campo

    def _mostrar_sedes(self):
        self._seleccionar_menu("sedes")
        self._limpiar_contenido()

        self._crear_titulo(
            "Administrar sedes",
            "Registrá nuevas sedes y consultá las existentes"
        )

        panel = tk.Frame(
            self._contenido,
            bg=self._fondo
        )
        panel.pack(fill="both", expand=True)

        # FORMULARIO
        formulario = tk.Frame(
            panel,
            bg="white",
            width=298,
            highlightbackground="#D9EAF4",
            highlightthickness=1
        )
        formulario.pack(
            side="left",
            fill="y",
            padx=(0, 16)
        )
        formulario.pack_propagate(False)

        tk.Label(
            formulario,
            text="Nueva sede",
            bg="white",
            fg=self._azul,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(12, 2))

        campos = tk.Frame(
            formulario,
            bg="white"
        )
        campos.pack(fill="x", padx=20)

        self._id_sede = self._crear_campo(
            campos, "ID de la sede"
        )

        self._nombre = self._crear_campo(
            campos, "Nombre"
        )

        self._direccion = self._crear_campo(
            campos, "Dirección"
        )

        self._telefono = self._crear_campo(
            campos, "Teléfono"
        )

        self._horarios = self._crear_campo(
            campos, "Horarios"
        )

        tk.Button(
            formulario,
            text="Guardar sede",
            command=self._guardar_sede,
            bg="#62BDEC",
            fg="#083756",
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            pady=10,
            cursor="hand2"
        ).pack(fill="x", padx=20, pady=(12, 12))

        # LISTADO
        listado = tk.Frame(
            panel,
            bg="white",
            highlightbackground="#D9EAF4",
            highlightthickness=1
        )
        listado.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            listado,
            text="Sedes registradas",
            bg="white",
            fg=self._azul,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=18, pady=(13, 10))

        # BOTONES ARRIBA DE LA TABLA
        acciones = tk.Frame(
            listado,
            bg="white"
        )
        acciones.pack(
            fill="x",
            padx=12,
            pady=(0, 10)
        )

        self._crear_boton_accion(
            acciones,
            "Ver detalles",
            self._ver_detalles_sede,
            "#E4F2FC",
            self._azul
        )

        self._crear_boton_accion(
            acciones,
            "Dar de baja",
            self._dar_de_baja_sede,
            "#F5D9D9",
            "#8B3030"
        )

        self._crear_boton_accion(
            acciones,
            "Reactivar",
            self._reactivar_sede,
            "#DDF2E4",
            "#286B43"
        )

        # TABLA DE SEDES
        tabla_frame = tk.Frame(
            listado,
            bg="white"
        )
        tabla_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        columnas = (
            "id",
            "nombre",
            "direccion",
            "estado"
        )

        self._tabla_sedes = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            style="Sedes.Treeview"
        )

        for columna, titulo, ancho in (
            ("id", "ID", 45),
            ("nombre", "Nombre", 135),
            ("direccion", "Dirección", 165),
            ("estado", "Estado", 90)
        ):
            self._tabla_sedes.heading(
                columna,
                text=titulo
            )
            self._tabla_sedes.column(
                columna,
                width=ancho,
                minwidth=45
            )

        barra = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self._tabla_sedes.yview
        )

        self._tabla_sedes.configure(
            yscrollcommand=barra.set
        )

        barra.pack(side="right", fill="y")

        self._tabla_sedes.pack(
            side="left",
            fill="both",
            expand=True
        )

        self._actualizar_tabla()

    def _crear_boton_accion(self, padre, texto, accion, fondo, color):
        tk.Button(
            padre,
            text=texto,
            command=accion,
            bg=fondo,
            fg=color,
            font=("Segoe UI", 9),
            relief="flat",
            borderwidth=0,
            pady=9,
            cursor="hand2"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=3
        )

    def _actualizar_tabla(self):
        for fila in self._tabla_sedes.get_children():
            self._tabla_sedes.delete(fila)

        for sede in consultar_sedes():
            estado = "Activa" if sede[5] == 1 else "Dada de baja"

            self._tabla_sedes.insert(
                "",
                "end",
                values=(
                    sede[0],
                    sede[1],
                    sede[2],
                    estado
                )
            )

    def _sede_seleccionada(self):
        seleccion = self._tabla_sedes.selection()

        if not seleccion:
            messagebox.showwarning(
                "Sin selección",
                "Seleccioná una sede de la tabla"
            )
            return None

        id_sede = int(
            self._tabla_sedes.item(
                seleccion[0],
                "values"
            )[0]
        )

        for sede in consultar_sedes():
            if sede[0] == id_sede:
                return sede

        messagebox.showwarning(
            "Sede no encontrada",
            "La sede ya no existe"
        )
        self._actualizar_tabla()

        return None

    def _ver_detalles_sede(self):
        sede = self._sede_seleccionada()

        if sede is None:
            return

        estado = "Activa" if sede[5] == 1 else "Dada de baja"

        texto = (
            "ID: " + str(sede[0]) + "\n"
            "Nombre: " + sede[1] + "\n"
            "Dirección: " + sede[2] + "\n"
            "Teléfono: " + sede[3] + "\n"
            "Horarios: " + sede[4] + "\n"
            "Estado: " + estado
        )

        messagebox.showinfo(
            "Datos de la sede",
            texto
        )

    def _guardar_sede(self):
        try:
            sede = Sede(
                int(self._id_sede.get()),
                self._nombre.get(),
                self._direccion.get(),
                self._telefono.get(),
                self._horarios.get()
            )

            if guardar_sede(sede):
                messagebox.showinfo(
                    "Sede registrada",
                    "La sede se guardó correctamente"
                )

                for campo in (
                    self._id_sede,
                    self._nombre,
                    self._direccion,
                    self._telefono,
                    self._horarios
                ):
                    campo.delete(0, tk.END)

                self._actualizar_tabla()

            else:
                messagebox.showwarning(
                    "ID duplicado",
                    "Ya existe una sede con ese ID"
                )

        except ValueError as error:
            messagebox.showerror(
                "Datos inválidos",
                str(error)
            )

    def _dar_de_baja_sede(self):
        self._cambiar_estado_sede(False)

    def _reactivar_sede(self):
        self._cambiar_estado_sede(True)

    def _cambiar_estado_sede(self, activar):
        datos = self._sede_seleccionada()

        if datos is None:
            return

        estado_actual = datos[5] == 1

        if estado_actual == activar:
            messagebox.showwarning(
                "Estado de sede",
                "La sede ya se encuentra en ese estado"
            )
            return

        if activar:
            pregunta = "¿Deseás reactivar esta sede?"
        else:
            pregunta = "¿Deseás dar de baja esta sede?"

        if not messagebox.askyesno(
            "Confirmar operación",
            pregunta
        ):
            return

        sede = Sede(
            datos[0],
            datos[1],
            datos[2],
            datos[3],
            datos[4]
        )

        if activar:
            sede.reactivar()
        else:
            sede.dar_de_baja()

        actualizar_estado_sede(sede)
        self._actualizar_tabla()

        messagebox.showinfo(
            "Operación realizada",
            "El estado se actualizó correctamente"
        )

    def ejecutar(self):
        self._ventana.mainloop()
