# BiblioRed — Sistema de préstamos interbibliotecarios

**Trabajo práctico integrador de Desarrollo de Aplicaciones con Objetos (DAO)** · UTN FRC · Grupo 73 · 2026.

Permite administrar sedes, socios, libros y ejemplares físicos; solicitar préstamos locales e interbibliotecarios; registrar remitos, devoluciones y reservas; consultar inventarios e historiales; y generar cuatro informes PDF. **No calcula multas**.

## Ejecutar el TP original

Requisitos: **Python 3.14**, **Flet 1.0.5**, **SQLite** (incluido en Python) y **ReportLab**.

Desde la terminal de VS Code, situada en la carpeta del proyecto:

```powershell
py -m pip install -r requirements.txt
py main.py
```

El punto de entrada es **`main.py`**. Crea las tablas que falten en SQLite y abre la aplicación Flet. No es necesario ejecutar cada módulo por separado.

## Organización del código

| Carpeta o archivo | Responsabilidad |
| --- | --- |
| `main.py` | Inicializa las tablas y abre la interfaz. |
| `clases/` | Objetos del dominio, reglas y patrones de diseño. |
| `servicios/` | Coordina procesos y validaciones; genera los informes PDF. |
| `datos/` | Persistencia: consultas, altas y modificaciones en SQLite. |
| `interfaces/` | Pantallas Flet, menú, formularios, listados y búsquedas. |
| `tests/` | Pruebas automatizadas y plan de verificación manual. |
| `docs/CORRESPONDENCIA_UML.md` | Relación entre el UML entregado y el código. |
| `imagenes/` | Recursos gráficos de la interfaz. |
| `scripts/` y `datos_demo/` | Utilidades opcionales de carga inicial; **no se ejecutan con `main.py`**. |

`interfaces/ventana_completa.py` administra la navegación; `interfaces/ventana_flet.py` es una clase **utilizada** como base de la interfaz y para sedes (su nombre es histórico). `ui_moderno.py` y `diseno_pantallas.py` contienen estilos y diseño compartido.

Las carpetas `clases`, `servicios`, `datos` e `interfaces` **no son programas independientes**, sino partes de BiblioRed.

## Base de datos

La aplicación usa **`biblioteca.db`** en la raíz del proyecto. Contiene **12 tablas**: `sedes`, `socios`, `libros`, `ejemplares`, `solicitudes_prestamo`, `remitos`, `historial_remitos`, `prestamos`, `devoluciones`, `remitos_retorno`, `historial_retornos` y `reservas`.

El archivo `biblioteca.db` **no se sube a GitHub** y nunca se debe borrar para limpiar código: hacerlo podría perder los préstamos, remitos y socios cargados en esa computadora. Para respaldarlo, cerrá la aplicación y copiá el archivo a otra ubicación.

La interfaz llama a servicios; los servicios usan funciones de `datos/` que ejecutan SQL con `sqlite3`. Las clases del dominio no abren conexiones por sí mismas.

## Patrones de diseño

- **State**, `clases/estado_remito.py` y `clases/remito.py`: estados `EstadoEmpaquetado`, `EstadoEnTransito` y `EstadoRecibido`. El remito delega en el estado actual y registra el historial. Se reutiliza para ida y retorno.
- **Strategy**, `clases/estrategia_plazo.py` y `clases/prestamo.py`: vencimiento de préstamos con estrategias intercambiables de 7, 14 o 21 días.

El documento UML entregado por el grupo se relaciona con la implementación mediante `docs/CORRESPONDENCIA_UML.md`. El UML **no reemplaza al diagrama entidad-relación (DER)** de SQLite.

## Reportes PDF

Desde **Consultas y análisis → Reportes**, se generan los cuatro informes:

1. Préstamos activos y vencidos por sede.
2. Libros más solicitados para préstamos interbibliotecarios.
3. Disponibilidad de títulos y ejemplares por sede.
4. Movimientos entre sedes y tiempo promedio de tránsito.

La generación está en `servicios/reportes_pdf.py` y las consultas SQL en `datos/consultas_bibliored_datos.py`. Los archivos se guardan en **`reportes_generados/`**.

Los gráficos se muestran solo cuando existen valores positivos. Si el informe contiene ceros, presenta indicadores y tabla sin inventar préstamos. La carpeta `reportes_generados/` puede regenerarse, pero conviene conservar los PDF que vayas a presentar.

## ISBN y ejemplares

Los nuevos libros validan **ISBN-13** con dígito de control; se pueden escribir con espacios o guiones y se normalizan. El ISBN identifica una edición de la publicación; el **código del ejemplar** identifica una copia física concreta. No se alteran automáticamente ISBN antiguos que ya estuvieran en la base.

## Pruebas

```powershell
py -m unittest discover -s tests -v
```

Las pruebas usan bases temporales; no modifican `biblioteca.db`. El plan de pruebas visuales está en `tests/PLAN_DE_PRUEBAS.md`. También hay un workflow en `.github/workflows/`.

## Archivos que se deben conservar y archivos generados

**Conservar:** `main.py`, `requirements.txt`, `clases/`, `servicios/`, `datos/`, `interfaces/`, `tests/`, `docs/CORRESPONDENCIA_UML.md`, `imagenes/`, `.github/`, `.git/` y, en tu computadora, **`biblioteca.db` y sus respaldos**.

**Generados automáticamente:** `__pycache__/`, `*.pyc`, carpetas de entornos virtuales y `reportes_generados/`. Son archivos locales ignorados por Git; no hay necesidad de incluirlos en una entrega de código fuente. No elimines los informes que debas mostrar.

**No eliminar por su nombre:** `interfaces/ventana_flet.py`, `datos/remito_modelo.py`, las tablas de retorno ni las clases de State/Strategy. Son parte de la implementación y del diseño defendido.
