# Correspondencia con el PDF entregado

Referencia: **BiblioRed final final.pdf**, páginas 3 a 5. El documento
entregado no se modifica: el código se adapta a él.

## State y movimientos

- `clases/remito.py`: único contexto `Remito`, con `TipoRemito.IDA` o
  `TipoRemito.RETORNO`, ejemplar, sedes, estado actual e historial.
- La referencia de ida es `id_solicitud`; la de retorno, `id_devolucion`.
  El constructor exige exactamente la referencia correspondiente al tipo (XOR).
- `despachar(fecha_hora)` y `recibir(fecha_hora)` delegan en `EstadoRemito`.
  `cambiar_estado(nuevo, fecha_hora)` registra un `HistorialRemito` y no permite
  saltar estados. `codigo()` devuelve `CodigoEstadoRemito`.
- `EstadoEmpaquetado` permite despachar; `EstadoEnTransito`, recibir;
  `EstadoRecibido` es terminal. Las operaciones inválidas no agregan movimientos.
- `HistorialRemito` contiene identificador, estado, fecha/hora y observación.
  La colección se expone como tupla y sus movimientos son inmutables.

## Strategy y operaciones del dominio

- `SolicitudPrestamo.confirmar_entrega()` genera un `Prestamo` y cambia la
  solicitud a prestada. Una solicitud interbibliotecaria requiere recepción.
- `Prestamo` tiene `fecha_entrega` y delega `calcular_vencimiento()` a
  `EstrategiaPlazo`: `Plazo7Dias`, `Plazo14Dias` o `Plazo21Dias`.
- `Prestamo.registrar_devolucion()` genera `Devolucion` y cierra el préstamo.
- `Reserva` tiene fecha, estado y las operaciones `atender()` y `cancelar()`.
- `Ejemplar` distingue `id_sede_propietaria` de `id_sede_actual`.
- `Sede.contacto` expone el teléfono de contacto. Los estados y tipos de valor
  nombrados en el diagrama están definidos en `clases/tipos.py`.

Las operaciones se usan dentro de las transacciones de `datos/`, junto con
las validaciones de socio habilitado, sedes activas, ubicación, duplicados y
prioridad de reservas. Las clases de dominio no abren conexiones SQLite.

## Representación en SQLite

El diagrama es de clases, no un esquema de tablas. Para conservar las bases
existentes y sus historiales, no se renombran ni se fusionan tablas:

| Concepto UML | Persistencia existente |
| --- | --- |
| Remito de ida | `remitos` / `historial_remitos` |
| Remito de retorno | `remitos_retorno` / `historial_retornos` |
| HistorialRemito.id_movimiento | `id_historial` de su tabla |
| HistorialRemito.fecha_hora | `fecha` del historial |
| Prestamo.fecha_entrega | `prestamos.fecha_prestamo` |
| Reserva.fecha | `reservas.fecha_reserva` |
| Sede.contacto | `sedes.telefono` |
| Ejemplar.sede_propietaria | `ejemplares.id_sede` |
| Ejemplar.ubicacion_actual | `ejemplares.id_sede_actual` |

Las asociaciones persistidas se representan mediante identificadores y claves
foráneas (`id_socio`, `id_libro`, etc.). Los identificadores de remitos y
movimientos pertenecen a su tabla: para recuperar un remito se proporciona
también `TipoRemito`. `datos/remito_modelo.cargar_remito()` reconstruye el
mismo objeto de dominio y su historial para cualquiera de los dos tipos.
No existe una clase de dominio `RemitoRetorno`.

Las fechas de dominio son `date` y las de movimientos `datetime`. Se serializan
en formato ISO al guardar en SQLite. Los tipos enumerados conservan los textos
existentes para no cambiar las consultas ni las pantallas.

## Verificación

```powershell
python -m unittest discover -s tests -v
```

Las pruebas usan bases temporales; no modifican `biblioteca.db`.
