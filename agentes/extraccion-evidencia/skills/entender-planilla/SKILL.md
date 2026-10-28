---
name: entender-planilla
description: Revisa el formato real de una planilla (columnas, listas de validación, filas modelo) antes de escribir en ella, usando lecturas pequeñas. Úsalo cuando cambie la planilla, haya una pestaña nueva, una vacuna nueva o dudes de una columna.
---

# Entender una planilla sin gastar tokens

Primero lee lo ya documentado (`docs/planillas/*.md`, `schemas/*.json`). Solo si falta algo, mira la planilla, siempre con lecturas acotadas.

## Procedimiento

1. **Pestañas e IDs**: `get_spreadsheet` con `fields: ["sheets.properties.title","sheets.properties.sheetId","sheets.properties.gridProperties.rowCount"]`.
2. **Encabezados**: `get_values` de la fila 1 completa (`A1:CJ1`). Nunca la pestaña entera.
3. **Listas de validación**: `get_spreadsheet` sobre una fila modelo (`ranges: ["Pestaña!A5:AM5"]`) con `fields: ["sheets.data.rowData.values.dataValidation.condition"]`. Cada columna con lista aparece con sus valores.
4. **Fórmulas**: mismo método con `fields: ["sheets.data.rowData.values.userEnteredValue"]` sobre la fila 1 (las fórmulas de las columnas generadas están en el encabezado como `ARRAYFORMULA`).
5. **Filas modelo**: para el formato "estándar" usa las filas con estado `Published` (hasta 3 por tipo). Para ubicarlas sin leer todo: lee solo la columna D (`D2:D800`) y filtra.
6. **Destino (`Tablas_capa_1`)**: lee las últimas 5 filas y 3 filas modelo de la misma sección con `A:K`. Para saber dónde termina la tabla usa `append_values`, que lo calcula solo.
7. **Registrar lo aprendido**: actualiza `docs/planillas/*.md` y `schemas/lists.json`; si una regla cambió, `/aprender-correccion`.

## Señales de alerta

- Una lista con valores que no están en `schemas/lists.json`: la planilla cambió; actualizar y avisar.
- Columnas nuevas o corridas: no escribir hasta confirmar el mapa.
- Una lectura de más de ~20.000 caracteres: probablemente leíste de más; acota el rango.
