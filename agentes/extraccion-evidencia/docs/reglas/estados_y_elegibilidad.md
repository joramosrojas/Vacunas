# Estados y elegibilidad

## Estados (columna D)

| Estado | Significado | Cuándo se usa |
|---|---|---|
| `Pending` | Pendiente de extraer (lo asigna el equipo) | No lo pone el agente |
| `Waiting` | Se intentó, falta información | Sin texto completo, falta decisión o dato; **siempre con nota en la celda D** |
| `Ok` | Extracción completa, sin dudas | Todos los campos obligatorios llenos y verificados |
| `Excluded` | No cumple criterios | Con nota en D explicando la razón |
| `Published` | Ya subido al tablero | No lo pone el agente |
| `Preprint`, `Repetido`, `OkA` | Casos especiales del equipo | No los pone el agente |

`Ok` significa "completado sin comentarios": si hay algo que el usuario deba decidir, no es `Ok`.

## Criterios de elegibilidad

Effectiveness (de la pestaña `Criterios de elegibilidad`): estudios **observacionales** que comparan vacunados con no vacunados, con desenlaces *contraer la enfermedad* y *contraer la enfermedad grave*. Se excluyen modelos matemáticos.

Extensión aceptada por el usuario (28 oct 2026): los estudios **antes y después** (programa de vacunación, ecológicos) que miden cuánto se redujo la enfermedad o la enfermedad grave **sí se incluyen**, usando la comparación `Pre-vaccination period versus post-vaccination period`. Ver `memoria/decisiones.md`.

## Se excluye cuando

1. **Producto no identificable.** El artículo no nombra la vacuna específica y no se puede inferir (ver `producto_vacuna.md`). Dejar `Vaccine` vacío, `Excluded` y nota en D.
2. **Producto fuera de la lista.** Ej. Varilrix (Oka/GSK): no está entre las vacunas de la planilla. `Vaccine` vacío, `Excluded`, nota.
3. Modelos matemáticos, reportes de casos, series de casos, protocolos sin resultados.
4. Estudios sin comparación ni medida de reducción.

## Se deja en Waiting cuando

- No se pudo acceder al texto completo (solo resumen o nada): llenar lo que el resumen permite y dejar nota "No se logró acceder al texto completo...".
- Hay una decisión pendiente que corresponde al usuario.

## Notas de celda

Se agregan con `updateCells` (campo `note`) sobre la celda D de la fila. Texto en español, una o dos frases: razón + dato clave (período, producto).
