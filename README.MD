# BiblioRed - Sistema de Préstamos Interbibliotecarios

Trabajo Práctico Integrador de DAO - UTN FRC - Grupo 73 (2026).

## Contrato de alcance
El documento de referencia es `BiblioRed_final_con_reportes.pdf` entregado por el grupo.
Incluye los diez procesos, State para remitos (ida/retorno), Strategy
para vencimientos de 7, 14 y 21 días, y cuatro reportes.
No incluye cálculo de multas.

## Tecnologías
Python 3.14, Flet 1.0.5, SQLite y ReportLab.

## Funcionalidades
Administrar sedes y socios, catálogo y ejemplares, solicitudes locales
e interbibliotecarias, remitos, préstamos efectivos, devoluciones,
reservas, disponibilidad por sede, inventario por código y sede,
historial de lecturas por socio y cuatro informes PDF.

Los cuatro informes son: préstamos activos y vencidos por sede,
libros más solicitados interbibliotecariamente, disponibilidad del
catálogo por sede y movimientos con tiempo promedio de tránsito.

## Ejecutar en Windows
```powershell
py -m pip install -r requirements.txt
py main.py
```

Los PDFs se generan en `reportes_generados/`. La base de datos local
`biblioteca.db` NO se sube a GitHub.

## Ejecutar pruebas (sin usar biblioteca.db)
```powershell
py -m unittest discover -s tests -v
```

## Diseño
- `clases/`: modelos de dominio, EstadoRemito y EstrategiaPlazo.
- `datos/`: consultas y operaciones SQLite.
- `servicios/`: casos de uso, generación de PDF.
- `interfaces/`: pantallas Flet.
- `main.py`: inicialización.

Al arrancar, el programa agrega automáticamente el campo
`observacion` a historiales existentes sin eliminar filas.
No se crean tablas nuevas para los patrones: son clases de dominio.

## Verificación
Las pruebas automatizadas cubren reglas de prioridad, estados,
vencimientos, integridad básica, consultas y migraciones.
La interfaz gráfica y un recorrido completo con datos reales
se deben verificar también en la aplicación local.
