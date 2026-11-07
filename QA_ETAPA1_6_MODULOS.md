# BiblioRed — cierre de los primeros seis módulos

**Contrato:** documento «BiblioRed final final.pdf» del Grupo 73, alcance 1–5,
más pantalla de Inicio. El PDF sigue siendo la referencia; este archivo
describe cómo comprobar la implementación, no agrega procesos.

## Preparación

1. Cerrar la aplicación.
2. Respaldar **fuera del repositorio** la base: `Copy-Item .\biblioteca.db ..\biblioteca_respaldo_etapa1.db`.
3. Ejecutar `py -m unittest discover -s tests -v`, luego `py main.py`.
4. No usar datos personales reales. No borrar historial de préstamos.

## Comprobación visual y funcional (Windows / Flet 1.0.5)

Marcar cada verificación después de **verificarla en la aplicación**, no
solo porque haya aprobado GitHub Actions.

### 1. Inicio

- [ ] Abre sin recuadros grises ni contenido cortado.
- [ ] Muestra métricas correctas: sedes activas, socios, préstamos activos y
      reservas pendientes.
- [ ] Cada acceso rápido abre su pantalla y el menú marca la opción activa.

### 2. Administrar sedes

- [ ] Se ven ID, teléfono, nombre, dirección, días, horas, casilla «24 horas»
      y botón «Guardar sede» sin que quede oculto el título.
- [ ] Buscar por ID parcial, nombre o dirección filtra sin lupa y con Enter.
- [ ] Editar sede **9001**, modificar teléfono y guardar; el horario anterior
      queda intacto si no se cambia.
- [ ] Dar de baja **9001** y comprobar que no pueda elegirse como origen o
      destino para nuevos trámites. Reactivarla al finalizar.
- [ ] «Viernes a lunes» es válido; un turno 18:00–09:00 indica «día
      siguiente»; horas iguales se rechazan salvo casilla explícita 24 horas.
- [ ] Los iconos Ver, Editar y Baja/Reactivar se ven enteros y ejecutan la
      operación indicada por su ayuda emergente.

### 3. Administrar socios

- [ ] El listado, los campos y los iconos Ver/Editar/Habilitar quedan visibles.
- [ ] Buscar por «j», «1» o parte de un apellido filtra al escribir y con Enter.
- [ ] Registrar un documento nuevo y verificar rechazo del duplicado.
- [ ] Editar teléfono/correo, inhabilitar el socio, verificar que ya no aparezca
      en nuevas solicitudes y volver a habilitarlo.

### 4. Catálogo y ejemplares

- [ ] Crear «Libro de prueba DAO», ISBN de prueba `9780000000001`, autor y
      editorial ficticios; intentar repetir el ISBN y comprobar el rechazo.
      Si ese ISBN ya existe, usar otro de prueba que no esté registrado.
- [ ] Crear ejemplar físico con código `ETAPA1-EJ-01` y sede activa 9001.
      Intentar repetir el código y comprobar el rechazo.
- [ ] Los títulos, ISBN, sede propietaria, estado y acciones se ven completos.
- [ ] Verificar que un ejemplar «En revisión» no aparece como disponible ni
      puede utilizarse para una solicitud nueva.
- [ ] Buscar libros y ejemplares por una sola letra y por parte del código;
      Enter funciona también.

### 5. Solicitudes de préstamo

- [ ] Con el ejemplar de prueba disponible en la sede 9001, crear solicitud
      **local** para un socio habilitado con destino 9001: tipo «Local».
- [ ] Comprobar que la copia no pueda solicitarse dos veces y luego cancelar
      esa solicitud; la copia vuelve a estar disponible.
- [ ] Crear solicitud **interbibliotecaria** con la misma copia (origen 9001)
      y destino a una sede activa distinta: el tipo es «Interbibliotecario».
- [ ] La solicitud aparece con socio, ejemplar, origen, destino, tipo y estado.
- [ ] Las sedes inactivas y los socios inhabilitados no aparecen como opciones
      válidas para nuevas solicitudes.

### 6. Remitos y traslados

- [ ] La solicitud interbibliotecaria aparece entre las pendientes de traslado.
- [ ] «Empaquetar» genera un único remito y deja la copia «Empaquetado».
- [ ] «Despachar» cambia a «En tránsito» y «Confirmar recepción» a «Recibido».
- [ ] No permite repetir el despacho ni la recepción de un remito ya finalizado.
- [ ] **Ver historial** muestra los tres movimientos, fecha y observación.
- [ ] Al recibir, la ubicación registrada del ejemplar es la sede destino.
      No aparece disponible para un préstamo directo desde el origen.

## Criterio de cierre

- Pruebas automáticas de GitHub Actions en verde.
- Los seis módulos se abren y muestran acciones completas en Windows.
- Se verifican manualmente los casos anteriores con datos ficticios.
- Si aparece una diferencia entre el PDF, el código y una captura, registrar
  cuál es y corregirla antes de declarar el módulo terminado.
- Los módulos restantes se verifican en una segunda etapa.
