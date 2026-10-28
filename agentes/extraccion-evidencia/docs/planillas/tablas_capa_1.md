# Destino final: pestaña `Tablas_capa_1`

## Dónde

| Planilla | ID | Uso |
|---|---|---|
| **`[Vacunas_2026] Información regulatoria y tablas de efectos`** | `1c3AlX5qPMxZTo55zsSEVTuC-C2m8mocgwyftxdy4Dus` | **Destino por defecto** ("la segunda planilla") |
| `[Vacunas_2025] Información regulatoria y tablas de efectos` | `1oX9SnslpAYXcnIhaJlf35FZIk1ysjdBAayXNbHI6daY` | Solo si el usuario lo pide |

Pestaña `Tablas_capa_1`, `sheetId` 1851227287 en ambas. Fila 1 = encabezados. La pestaña tiene unas 2.200 filas: **nunca leerla completa**.

## Columnas

| Col | Encabezado | Contenido |
|---|---|---|
| A | Vacuna | Nombre de visualización (ver abajo) |
| B | Sección | `Effectiveness`, `Post-authorization safety`, `Clinical efficacy`, `Safety`, `Immunogenicity`, `Booster` |
| C | Outcome | Effectiveness: `Contracting disease` / `Contracting severe disease`. Seguridad: `Comparative` / `Non-comparative` / `Country reports` |
| D | Group | `Overall` o subgrupo. En seguridad comparativa = nombre del evento (ej. `Myocarditis/pericarditis`) |
| E | Study design and number of participants | Inglés |
| F | Country, follow-up and outcome definition | Inglés |
| G | Main results | Inglés |
| H | Diseño del estudio y número de participantes | Español |
| I | País, seguimiento y definición de resultados | Español |
| J | Resultados principales | Español |
| K | Fecha | Fecha de carga, formato `28 Octubre 2026` (día, mes con mayúscula en español, año) |

Una fila por **desenlace** y por **grupo**: un artículo con enfermedad y enfermedad grave genera 2 filas.

## Nombres de vacuna (columna A)

Patrón: `<Marca> <enfermedad> vaccine`. Existentes: `Abrysvo RSV vaccine`, `Dengvaxia`, `Qdenga`, `STAMARIL`, `Ixchiq chikungunya vaccine`, `Imvanex - Jynneos mpox vaccine`, `Measles, mumps and rubella vaccine`, `Comirnaty/Pfizer-BNT162b2 COVID-19 vaccine`, `Spikevax/Moderna COVID-19 vaccine`, `CoronaVac/Sinovac COVID-19 vaccine`, `Convidecia/CanSino COVID-19 vaccine`, `Nuvaxovid - Novavax/Serum Institute of India COVID-19 vaccine`, `Corbevax COVID-19 vaccine`. Varicela: `Varivax varicella vaccine`. La tabla de equivalencias planilla -> visualización está en `schemas/lists.json` (`vaccine_display`).

## Formato de las celdas en inglés (effectiveness)

**E (diseño y participantes)**
```
<Diseño con mayúscula inicial>

Comparison: <comparación en minúscula>

[<Autor, año>]
[<Episte ID>]

<N> individuals aged <edad>

<n grupo 1> <unidad 1 en minúscula>
<n grupo 2> <unidad 2 en minúscula>
```
Si no hay conteos de grupos, se omite el último bloque; si no hay N, "Individuals of all ages".

**F (país, seguimiento y definición)**
```
<País>

Data from <fuente>.

Observation period: <período>.

Contracting the disease was measured as <definición>.
```
En estudios ecológicos (antes/después) la última frase es `Disease occurrence was measured as ...`.

**G (resultados)**
- VE/RR/OR con IC: `VE: 79% (95% CI: 66 - 88)`
- Dos dosis: `VE:\n1 dose: 85.4% (95% CI: 80.8 - 88.9)\n2 doses: 89.1% (95% CI: 83.8 - 92.7)`
- Reducción de tasa (antes/después), como la fila de Gentile: `Reduction in hospitalization rate:\nIRR: 65% (95% CI: Not reported)\nRate per 100,000 child-years: 15.7 (before licensure) vs 5.5 (after licensure); RR: 2.9 (95% CI: 2.4 - 3.6)`
- Sin IC en el artículo: `(95% CI: Not reported)`. No inventar ni calcular IC propios.
- Varios grupos (comunidades, temporadas): líneas en la misma celda.

## Formato en español (H, I, J)

Traducción completa de E, F y G (no se deja nada en inglés salvo siglas y nombres propios): decimales con coma ("85,4%") y miles con punto ("85.050"); `VE` -> `EV`; `95% CI` -> `IC del 95%`; `Not reported` -> `no reportado`. Glosario en `docs/reglas/traduccion_es.md`.

## Seguridad post-autorización

- **Comparativa**: C = `Comparative`, D = evento. E = diseño + comparación + referencia + participantes. G = `Rate ratio: 1.04% (95% CI: 0.88 - 1.23)` o con primera y segunda dosis:
  `First dose: \nSIR 0.74 (95% CI: 0.33 - 1.64)\n\nSecond dose:\nSIR: 1.73 (95% CI: 0.93 - 3.22)`.
- **No comparativa**: C = `Non-comparative`, D = `Overall`. E = `[Autor, año]\n\n[Episte ID]`. F = `<N> participants\n\nNon-comparative study\n<País>\n\nThe study described ...\n\nThe study reported ...`. G = `NA` (en español `N / A`).
- **Reportes de país**: C = `Country reports`; no se generan desde artículos.

## Cómo se agrega

1. Usar `append_values` sobre `Tablas_capa_1!A<última fila>` (agrega después de la tabla), las 11 columnas A:K de una sola vez.
2. Releer A:C y K de las filas nuevas y comparar con lo enviado. Si el número de filas no coincide, parar y avisar.
3. No tocar ni borrar la fila a medio llenar que a veces queda al final (suele tener solo la vacuna en A y fórmulas `GOOGLETRANSLATE` en H:J) salvo que el usuario lo pida. Otras personas pueden borrarla mientras se trabaja: por eso los ajustes posteriores se hacen **releyendo la posición actual**, no por números de fila recordados.
4. `tools/render_tablas.py` genera las 11 columnas desde el registro validado.
