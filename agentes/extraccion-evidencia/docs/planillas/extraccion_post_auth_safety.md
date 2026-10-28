# Planilla de extracción: pestaña `Post_authorization_safety`

## Identificación

- Planilla de extracción: `[Vacunas_2026] Data extraction sheet for updates`, ID `1HR1gwLKPmeZzJlTANbaRDwO2BkpsfFyH_bc2aldoHfs`.
- Más IDs y `sheetId` por pestaña: `schemas/sheets.json`.
- Pestaña: `Post_authorization_safety` (`sheetId` 1143188798). Fila 1 = encabezados.
- La misma fila sirve para estudios **comparativos** (columna U = Yes) y **no comparativos** (columna BO = Yes). Nunca ambos.

## Qué llena el agente

C, D, I:Y.. según el caso (ver mapa). Las columnas desde BR en adelante son fórmulas o texto generado: no escribir.

## Mapa de columnas

| Col | Encabezado |
|---|---|
| A | Id |
| B | Author and year |
| C | Assigned to |
| D | Status |
| E | Fecha asignación |
| F | Title |
| G | Doi |
| H | Type of article |
| I | Vaccine |
| J | Study design |
| K | Comparison |
| L | Number of participants |
| M | Individuals aged  (e.g."18 years and older" or "18 to 64 years"): |
| N | Unit of intervention |
| O | Number intervention/case group: |
| P | Unit of control |
| Q | Number control group |
| R | Country/ies |
| S | Data from (database): |
| T | Observation period  (from month day, year to month day, year) |
| U | Comparative study |
| V | Outcome 1 |
| W | Outcome was measured as  (if comparative) |
| X | Effect measure (RR/OR/HR/IRR) |
| Y | Point estimate (first dose): |
| Z | Lower bound  (first dose): |
| AA | Upper bound  (first dose): |
| AB | Point estimate (second dose): |
| AC | Lower bound  (second dose): |
| AD | Upper bound (second dose): |
| AE | Outcome 2 |
| AF | Outcome was measured as  (if comparative) |
| AG | Effect measure (RR/OR/HR/IRR) |
| AH | Point estimate (first dose): |
| AI | Lower bound  (first dose): |
| AJ | Upper bound  (first dose): |
| AK | Point estimate (second dose): |
| AL | Lower bound  (second dose): |
| AM | Upper bound (second dose): |
| AN | Outcome 3 |
| AO | Outcome was measured as  (if comparative) |
| AP | Effect measure (RR/OR/HR/IRR) |
| AQ | Point estimate (first dose): |
| AR | Lower bound  (first dose): |
| AS | Upper bound  (first dose): |
| AT | Point estimate (second dose): |
| AU | Lower bound  (second dose): |
| AV | Upper bound (second dose): |
| AW | Outcome 4 |
| AX | Outcome was measured as  (if comparative) |
| AY | Effect measure (RR/OR/HR/IRR) |
| AZ | Point estimate (first dose): |
| BA | Lower bound  (first dose): |
| BB | Upper bound  (first dose): |
| BC | Point estimate (second dose): |
| BD | Lower bound  (second dose): |
| BE | Upper bound (second dose): |
| BF | Outcome 5 |
| BG | Outcome was measured as  (if comparative) |
| BH | Effect measure (RR/OR/HR/IRR) |
| BI | Point estimate (first dose): |
| BJ | Lower bound  (first dose): |
| BK | Upper bound  (first dose): |
| BL | Point estimate (second dose): |
| BM | Lower bound  (second dose): |
| BN | Upper bound (second dose): |
| BO | Non-comparative study |
| BP | The study described ...[mini descripción del estudio, periodo de observación, fuente de información]: |
| BQ | The study reported... [mini descripción de los resultados - Reportar las incidencias y prevalencias de vigilancia pasiva]: |
| BR | Study design and number of participants |
| BS | Country, follow-up and outcome definition |
| BT | Main results |
| BU | Reference |
| BV | Study description and main results |
| BW | Study design and number of participants |
| BX | Country, follow-up and outcome definition |
| BY | Main results (pericarditis/miocarditis) |
| BZ | Study design and number of participants |
| CA | Country, follow-up and outcome definition |
| CB | Main results (CVST) |
| CC | Study design and number of participants |
| CD | Country, follow-up and outcome definition |
| CE | Main results (GB syndrome) |
| CF | Study design and number of participants |
| CG | Country, follow-up and outcome definition |
| CH | Main results (MI syndrome) |

## Listas de validación

| Columna | Valores permitidos |
|---|---|
| K Comparison | Vaccinated versus unvaccinated; Pre-vaccination period versus post-vaccination period; NA |
| N Unit of intervention | Cases, Vaccinated, Doses administered, Controls |
| P Unit of control | Unvaccinated, Controls, NA |
| U Comparative study / BO Non-comparative study | Yes, No |
| V (Outcome 1; igual para Outcome 2 a 5) | Myocarditis/pericarditis; Guillain-Barré syndrome; Thrombosis with thrombocytopenia syndrome; Capillary leak syndrome; Cerebral venous sinus thrombosis without thrombocytopenia; Menstrual disorders; Multisystem inflammatory syndrome; Cutaneous small-vessel vasculitis; Autoimmune hepatitis; Disseminated intravascular coagulation; Aseptic meningitis; mumps cases; Stillbirth; Spontaneous Abortion/Miscarriage; Antenatal hemorrhage; Preeclampsia/Eclampsia; Fetal Vaccinia (congenital infection); Congenital anomalies; Preterm delivery/birth; Anaphylaxis; Ophthalmologic Ocular Manifestations; NA |
| X Effect measure | RR, OR, HR, IRR, RI, Rate ratio, SIR, NA, ROR, OE ratio |

(`schemas/lists.json` es la fuente única.)

## Cómo se llena según el tipo

**Comparativo** (U = Yes, BO = No): rellenar K (comparison), N:Q (grupos), un bloque por desenlace (hasta 5): desenlace (lista), "measured as", medida de efecto, estimador con IC para primera y segunda dosis. BP y BQ quedan vacíos.

**No comparativo** (U = No, BO = Yes): K = NA; N = Cases/Vaccinated/Doses administered; P = NA. Completar BP ("The study described ...": mini descripción con período y fuente) y BQ ("The study reported ...": incidencias y proporciones reportadas). Los bloques de desenlace quedan vacíos.

Ejemplos de referencia: `memoria/casos_resueltos.md` (fila 2 comparativa; fila 4 no comparativa).
