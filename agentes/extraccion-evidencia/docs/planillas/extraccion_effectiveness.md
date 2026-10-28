# Planilla de extracción: pestaña `Effectiveness`

## Identificación

- Planilla de extracción: `[Vacunas_2026] Data extraction sheet for updates`, ID `1HR1gwLKPmeZzJlTANbaRDwO2BkpsfFyH_bc2aldoHfs`.
- Más IDs y `sheetId` por pestaña: `schemas/sheets.json`.
- Pestaña: `Effectiveness` (`sheetId` 1290642341). Fila 1 = encabezados. Una fila por artículo y vacuna.
- Las filas son **estudios**; el mismo artículo puede repetirse por vacuna (mismo Episte ID en la columna A).

## Qué llena el agente

Columnas **C** (Assigned to) y **D** (Status), y **I:AM** (datos). No escribir en A:B, E:H ni en **AN:AY** (son fórmulas).

## Mapa de columnas

| Col | Encabezado |
|---|---|
| A | ID |
| B | Author, year |
| C | Assigned to |
| D | Status |
| E | Fecha asignación |
| F | Title |
| G | DOI |
| H | Type of articles |
| I | Vaccine |
| J | Study design |
| K | Comparison |
| L | Number of participants |
| M | Individuals aged  (e.g."18 years and older"): |
| N | Unit of intervention |
| O | Number intervention/case group: |
| P | Unit of control |
| Q | Number control group |
| R | Country/ies |
| S | Data from (database): |
| T | Observation period  (from month day, year to month day, year) |
| U | Variant |
| V | Contracting the disease was measured as: |
| W | Unit of measure |
| X | Point estimate (second dose): |
| Y | Lower bound  (second dose): |
| Z | Upper bound (second dose): |
| AA | Unit of measure |
| AB | Point estimate (first dose): |
| AC | Lower bound  (first dose): |
| AD | Upper bound  (first dose): |
| AE | Contracting severe disease was measured as: |
| AF | Unit of measure |
| AG | Point estimate (second dose): |
| AH | Lower bound  (second dose): |
| AI | Upper bound (second dose): |
| AJ | Unit of measure |
| AK | Point estimate (first dose): |
| AL | Lower bound  (first dose): |
| AM | Upper bound  (first dose): |
| AN | Study design and number of participants |
| AO | Country, follow-up and outcome definition |
| AP | Main results  (contracting the disease) |
| AQ | Study design and number of participants |
| AR | Country, follow-up and outcome definition (severe) |
| AS | Main results  (contracting severe disease) |
| AT | Additional data for variants |

## Cómo se leen los pares dosis

- Los bloques "second dose" van **antes** que los de "first dose" en el encabezado (X:Z segunda dosis; AB:AD primera dosis).
- Período con una sola dosis (programa de 1 dosis) -> columnas *first dose*. Período con 2 dosis -> *second dose*.
- Estudios sin separación por dosis: usar *second dose* (columna X/AG) y aclarar en el texto "measured as".
- Resultados con varias líneas (varios grupos, comunidades o temporadas): **todo en una sola celda**, en X (enfermedad) o AG (enfermedad grave). La fórmula deja pasar el texto tal cual si contiene un salto de línea.

## Listas de validación (modo estricto: no se puede escribir texto libre)

| Columna | Valores permitidos |
|---|---|
| C Assigned to | JT, SF, CV, SP, AMR, FC, FN |
| D Status | Ok, Pending, Waiting, Preprint, Excluded, Published, Repetido, OkA |
| I Vaccine | BNT162b2, BNT162b2 bivalent, Spikevax/Moderna COVID-19 vaccine, Sinovac, Novavax, MMR, Dengvaxia, MVA-BN, Abrysvo, Ixchiq, Qdenga (TAK-003), SKYVaricella, Varivax |
| K Comparison | Vaccinated versus unvaccinated; Pre-vaccination period versus post-vaccination period |
| N Unit of intervention | Cases, Vaccinated, Doses administered |
| P Unit of control | Unvaccinated, Controls, NA, Doses administered |
| W, AA, AF, AJ Unit of measure | VE, RR, OR, IRR, HR |

Las listas completas y actualizadas están en `schemas/lists.json` (fuente única para `tools/validate_record.py`).

## Columnas generadas (AN:AY)

Las fórmulas arman el texto preliminar en inglés: diseño + comparación + `[Autor]` + `[Episte ID]` + "N individuals aged M" + grupos; país + "Data from" + período + "measured as"; resultados. Sirven de borrador, no de producto final: el formato definitivo está en `docs/planillas/tablas_capa_1.md`.

## Formato de los valores (estándar = filas `Published`)

- Diseño en minúscula inicial y descriptivo ("test-negative case-control study", "retrospective cohort study").
- Edad: "18 years and older", "5 years or younger", "13 years and younger", "all ages", "NR" si no se reporta.
- País en inglés y completo ("United States", no "USA").
- Período: "January 1, 2018 to November 30, 2024" o "2022-2024".
- "measured as": frase corta, sin comentarios del agente.
- Estimadores numéricos limpios (sin texto). Un porcentaje de reducción en estudios antes/después va con unidad `IRR`.
- Celdas sin dato: vacías. Si el artículo no reporta IC: dejar vacío el límite; en la tabla final se escribe "95% CI: Not reported".
- `Status`: ver `docs/reglas/estados_y_elegibilidad.md`. `Assigned to`: la sigla de quien asigna el usuario (por defecto JT).
- Nota de celda (clic derecho > insertar nota) en D para explicar exclusiones o falta de texto completo.
