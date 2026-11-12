# Mejoras solicitadas para la defensa (revisión)

## Qué cambió
- **ISBN-13:** el dominio valida 13 dígitos y su dígito de control; acepta guiones/espacios de entrada y conserva el formato numérico normalizado. La restricción `UNIQUE` continúa vigente.
- **Reportes:** `servicios/reportes_pdf.py` agrega un gráfico de barras horizontal a cada uno de los cuatro reportes, además de la tabla existente. El gráfico muestra hasta ocho categorías para conservar la legibilidad.
- **Más operaciones para mostrar:** `scripts/preparar_demo_reportes.py` crea una **base nueva** con 18 préstamos, sus solicitudes, remitos y devoluciones de prueba.

## Cómo probar SIN modificar tu biblioteca.db

Desde la raíz del repositorio:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py -m scripts.preparar_demo_reportes
```

Esto crea `biblioteca_reportes_demo.db` sin tocar `biblioteca.db`. Si ya existe, el comando se detiene para evitar sobrescribirla.

**Para que la app use los datos de demostración**, cerrarla primero y hacer una copia de seguridad de la base real *fuera de la carpeta del repo*:

```powershell
Copy-Item .\biblioteca.db ..\biblioteca_respaldo_antes_de_demo.db
Copy-Item .\biblioteca_reportes_demo.db .\biblioteca.db
py main.py
```

Importante: la segunda instrucción de copia **reemplaza** la base habitual, por eso es obligatorio respaldarla primero. Hacerlo solamente si se quiere cambiar a la base de demostración y el programa está cerrado. Para restaurar:

```powershell
Copy-Item ..\biblioteca_respaldo_antes_de_demo.db .\biblioteca.db
```

## Verificación de la defensa
1. Abrir los formularios en ventana normal y maximizada: comprobar controles y acciones.
2. Generar los cuatro reportes; revisar los PDF creados en `reportes_generados/` y confirmar que tengan tabla y gráfico.
3. Mostrar consultas y ejemplo SQL en `datos/consultas_bibliored_datos.py`.
4. Mostrar el DER por separado: el UML entregado **no es un DER**.
5. Explicar las librerías: Flet (interfaces), sqlite3 (datos), ReportLab (reportes), abc (patrones).

La base y los movimientos son **ficticios para uso académico**, no datos operativos. No se generan multas. El cambio de ISBN no corrige bases locales ya existentes: si contienen ISBN inválidos, deben revisarse de manera explícita.
