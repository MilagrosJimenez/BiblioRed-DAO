# BiblioRed — Sistema de préstamos interbibliotecarios

Trabajo práctico integrador de **Desarrollo de Aplicaciones con Objetos** (DAO), UTN FRC, Grupo 73 — 2026.

El alcance está definido por el **documento de referencia de desarrollo entregado a la cátedra**. El programa incluye los ocho procesos obligatorios, inventario por códigos e historial de lecturas; cuatro reportes PDF y los patrones **State** (remitos) y **Strategy** (plazos). No se calculan multas.

## Cómo ejecutar

Se utiliza **Python 3.14**, **Flet 1.0.5**, **SQLite** y **ReportLab**.

En la terminal de VS Code, desde la carpeta del proyecto:

```powershell
py -m pip install -r requirements.txt
py main.py
```

**Punto de entrada:** `main.py`. Inicializa las tablas y abre la interfaz Flet. No hay que ejecutar cada archivo Python por separado.

## Estructura del proyecto

| Ruta | Para qué sirve |
| --- | --- |
| `main.py` | Inicia BiblioRed y prepara la base de datos. |
| `clases/` | Objetos del negocio: Sede, Socio, Libro, Ejemplar, Solicitud, Préstamo, Remito, Reserva y Devolución. También contiene las clases de los patrones State y Strategy. |
| `datos/` | Consultas y modificaciones de SQLite: guardar, consultar, actualizar y verificar estados. |
| `servicios/` | Coordina las reglas y los procesos del negocio; también genera los cuatro reportes PDF. |
| `interfaces/` | Pantallas Flet, navegación, formularios, listados y búsquedas. |
| `imagenes/` | Logo de UTN FRC. |
| `tests/` | Pruebas automatizadas y `PLAN_DE_PRUEBAS.md` para verificaciones manuales. |
| `.github/workflows/` | Ejecuta las pruebas en GitHub automáticamente. |

### Archivos especiales dentro de `interfaces/`

- `ventana_completa.py`: ventana principal, menú lateral e Inicio; conecta todas las pantallas.
- `ventana_flet.py`: base de la interfaz Flet y administración de sedes. Su nombre es histórico, pero **sí está en uso**.
- `ventana_socios.py`, `ventana_catalogo.py`, `ventana_solicitudes.py`, etc.: cada una presenta las operaciones del módulo correspondiente.
- `ui_moderno.py`: estilos y filtros de búsqueda compartidos.
- `diseno_pantallas.py`: distribución y tamaños comunes de formularios/listados.
- `busqueda_general.py`: busca **secciones del menú lateral** desde Inicio, no personas ni ejemplares.

Los nombres `clases`, `datos`, `servicios` e `interfaces` representan responsabilidades distintas. No son cuatro programas: son partes de la misma aplicación.

## Base de datos y archivos generados

- `biblioteca.db` guarda los datos reales de tu computadora; **no se sube a GitHub**.
- `reportes_generados/` aparece cuando se producen informes PDF; no hace falta subirlo.
- `__pycache__/` y archivos `.pyc` los crea Python automáticamente.
- `.venv/` o `venv/` son entornos de Python, si se utilizan.
- `.git/` es la carpeta de control de versiones. **No hay que borrarla.**

Estos archivos y carpetas locales generados automáticamente no son parte del código fuente.

## Cómo ejecutar las pruebas

```powershell
py -m unittest discover -s tests -v
```

Las pruebas automatizadas verifican reglas de negocio, integridad de SQLite, patrones de diseño y construcción de pantallas. También se deben probar las operaciones en Windows, porque las pruebas no garantizan por sí solas que todo se dibuje correctamente.

El plan de pruebas manuales de los doce módulos está en `tests/PLAN_DE_PRUEBAS.md`.

## Reportes y patrones de diseño

Los informes PDF previstos son: préstamos activos y vencidos por sede, libros más solicitados interbibliotecariamente, disponibilidad por sede y movimientos entre sedes con tiempo promedio de tránsito.

- `clases/estado_remito.py`: patrón **State**, cambios de estado de remitos.
- `clases/estrategia_plazo.py`: patrón **Strategy**, plazos de 7, 14 y 21 días.

Estas clases deben mantenerse porque forman parte del diseño que se defiende ante la cátedra.

## Entrega y demostración

La consigna de Biblioteca exige ocho procesos, sus validaciones, al menos
dos patrones de diseño y cuatro reportes no triviales. El documento del
Grupo 73 también incluye inventario por código e historial de lecturas.

Para verificar el proyecto desde una copia nueva:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py main.py
```

**Atención:** la base `biblioteca.db` local está excluida de GitHub.
Al ejecutar una copia nueva, `main.py` crea las tablas vacías. Para una
demostración completa se deben preparar en esa copia datos de ejemplo
(sedes activas, socios habilitados, libros y ejemplares), o usar una
base de demostración independiente, sin datos personales reales.

**Documento de referencia:** `BiblioRed final final.pdf` contiene el
alcance y el UML presentado. No forma parte de los archivos de código de
este repositorio; entregarlo por separado según indique la cátedra.
Antes de la entrega final, actualizar el diagrama para que represente
`Remito` y `RemitoRetorno` como contextos separados que reutilizan
`EstadoRemito`. En SQLite hay historiales diferenciados de ida y retorno.

### Qué mostrar en la defensa

1. Sedes, socios y catálogo; localizar un registro escribiendo DNI,
   título, ISBN o código, sin recorrer listas.
2. Solicitud interbibliotecaria; empaquetar, despachar y recibir el remito.
3. Entregar un préstamo y elegir la estrategia de 7, 14 o 21 días.
4. Registrar devolución en estado Bueno y completar el retorno a origen.
5. Consultar disponibilidad, reservas, inventario, historial y los
   cuatro reportes PDF.

No es necesario borrar las pruebas automatizadas: permiten verificar
reglas sin tocar la base de demostración. No se deben subir
`biblioteca.db`, `__pycache__/`, `.venv/` ni los PDF generados por la
aplicación.
