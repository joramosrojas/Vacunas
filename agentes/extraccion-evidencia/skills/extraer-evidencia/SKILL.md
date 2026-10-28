---
name: extraer-evidencia
description: Extrae datos de artículos de vacunas (effectiveness, seguridad post-autorización comparativa y no comparativa) a la planilla de extracción y a Tablas_capa_1. Úsalo cuando el usuario pida extraer filas Waiting/Pending, llenar columnas I:AM o pasar datos a las tablas de capa 1.
---

# Extraer evidencia (flujo del líder)

Tú eres el **líder**. Los trabajadores son los subagentes `fetcher`, `extractor`, `verifier`, `sheet-writer` (en `agentes/extraccion-evidencia/agents/`). Detalle del flujo: `docs/flujo.md`. Mantén tu contexto pequeño: no leas artículos completos ni hojas completas.

## Pasos

1. **Entender el pedido.** Tipo (`effectiveness`, `safety_comparative`, `safety_noncomparative`), vacuna, filas/estado, carpeta de Drive o textos pegados. Si falta la carpeta de PDFs, pídela una sola vez.
2. **Cargar contexto mínimo.** `memoria/correcciones.md` (solo `activa`) y el doc de reglas del tipo. No leas los otros tipos.
3. **Localizar.** Lanza `fetcher` con el filtro. Resultado: manifiesto. Pregunta al usuario solo por PDFs que falten o sean ambiguos; entre tanto avanza con los que sí están.
4. **Decidir paralelismo.** Menos de 3 artículos: extrae tú en línea siguiendo `agents/extractor.md`. 3 o más: un `extractor` por artículo en el mismo mensaje (máx. 5 a la vez).
5. **Validar.** Guarda los registros en `work/registros/<fecha>.json` y ejecuta `python3 agentes/extraccion-evidencia/tools/validate_record.py work/registros/<fecha>.json`. Devuelve los ERROR al extractor una vez.
6. **Verificar.** Lanza `verifier` sobre campos `low`, `flags` y una muestra del 20 % del resto. Aplica sus `changes` si la evidencia es clara; si no, pregunta al usuario con la cita.
7. **Estados.** Decide `Ok`/`Waiting`/`Excluded` con `docs/reglas/estados_y_elegibilidad.md`. `Ok` = sin comentarios pendientes.
8. **Escribir.** Lanza `sheet-writer` con los registros validados (y la fecha de hoy). No pidas permiso para escribir en las filas asignadas.
9. **Reportar.** Tabla corta: fila, artículo, estado, valores clave, celdas marcadas, filas añadidas a Tablas. Di explícitamente qué quedó en Waiting/Excluded y por qué, y qué verificaste releyendo.
10. **Aprender.** Si el usuario corrige algo, ejecuta `/aprender-correccion` antes de seguir.

## Reglas de oro

- Nunca digas que cambiaste algo que no ejecutaste o no releíste.
- Listas de validación: valor exacto o vacío.
- Las filas cambian: siempre por Episte ID.
- Sin texto completo no hay `Ok`: Waiting con nota.
- Una corrección del usuario manda sobre estas reglas hasta que se documente la excepción.
