
# BiblioRed - Sistema de Préstamos Interbibliotecarios

Trabajo Práctico Integrador de Desarrollo de Aplicaciones con Objetos (DAO).

UTN - Facultad Regional Córdoba | 2026

## Descripción

BiblioRed es un sistema desarrollado en Python para gestionar una red de bibliotecas, sus socios, libros, ejemplares y préstamos interbibliotecarios.

## Tecnologías

- Python 3.14
- Flet 1.0.5
- SQLite
- Programación Orientada a Objetos

## Funcionalidades implementadas

- Administración de sedes.
- Administración de socios.
- Catálogo de libros y ejemplares.
- Solicitudes de préstamo.
- Remitos y traslados interbibliotecarios.
- Préstamos efectivos.
- Devoluciones y remitos de regreso.

## Funcionalidades pendientes

- Reservas y consulta de disponibilidad.
- Reportes.
- Patrones de diseño obligatorios.
- Pruebas integrales y mejoras visuales.

## Instalación

1. Tener Python instalado.
2. Abrir una terminal en la carpeta del proyecto.
3. Instalar las dependencias:

    py -m pip install -r requirements.txt

4. Ejecutar la aplicación:

    py main.py

La base de datos SQLite se crea automáticamente al iniciar el sistema.

## Organización

- clases/: clases del dominio.
- datos/: persistencia con SQLite.
- servicios/: lógica de negocio.
- interfaces/: interfaz gráfica con Flet.
- imagenes/: recursos visuales.
- main.py: punto de entrada.

## Estado del proyecto

En desarrollo.
