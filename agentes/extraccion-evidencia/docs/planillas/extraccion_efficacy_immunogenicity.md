# Planilla de extracción: pestañas `Efficacy` e `Immunogenicity`

Planilla `[Vacunas_2026] Data extraction sheet for updates` (ID en `schemas/sheets.json`). Fila 1 = encabezados. Son ensayos (ECA): una fila por artículo y vacuna. Mapa verificado el 2026-10-28 contra filas reales (Weibel, Varis, Lassen, Richardson, Tindale). **Las filas no están donde uno las recuerda** (hay cientos de filas vacías entre bloques y el rango que devuelve la API no es la última fila con datos): ubicar siempre por Episte ID (columna A).

## `Efficacy` (`sheetId` 975072314)

| Cols | Contenido |
|---|---|
| A:K | A ID, B Author year, C Assigned to, D Status, E Fecha asignación, F Extracted, G Title, H DOI, I Type of articles, J Thread name, **K Vaccine** |
| L:N | L Trial name, M NCT, N Trial phase |
| O:T | O Number of participants, P Individuals aged, Q Number vaccinated, R Number placebo, S Country/ies, T Follow-up |
| U | Variant |
| V | Contracting the disease ... measured as |
| W:Z | Eventos y totales, **grupo general**: W events intervention, X total intervention, Y events comparison, Z total comparison |
| AA:AD, AE:AH, AI:AL, AM:AP, AQ:AT, AU:AX | Mismos 4 valores por subgrupo, en este orden: ≥60 años, **niños y adolescentes**, hombres, mujeres, embarazadas, VIH |
| AY | Contracting severe disease ... measured as |
| AZ:BC | Enfermedad grave, grupo general |
| BD:BG, BH:BK, BL:BO, BP:BS, BT:BW | Enfermedad grave por subgrupo: ≥60, niños y adolescentes, hombres, mujeres, embarazadas |
| BX | Mortality (BY:CB eventos y totales) |
| CC | Adverse events (any) measured as |
| CD:CG | Eventos adversos (cualquiera), grupo general |
| CH:CK | Eventos adversos (cualquiera), niños y adolescentes |
| CL:DE | Eventos adversos (cualquiera) por subgrupo: ≥60, hombres, mujeres, embarazadas, VIH |
| DF | Serious adverse events measured as (DG:DJ general; DK:DN niños; DO:DR ≥60; DS:DV hombres; DW:DZ mujeres; EA:ED embarazadas; EE:EH VIH) |
| EI:EZ | **Texto generado por fórmula** (diseño, país/seguimiento, resultados; errores `#DIV/0!` y `#NUM!` con ceros): no escribir y no copiar |

Trampas:
- Los datos de un estudio con participantes niños pueden estar en el bloque **niños y adolescentes** (AE:AH) y no en el general (W:Z). Leer las dos zonas.
- Los textos generados citan el estudio con `[]` vacíos y corchetes sin cerrar, y toman el seguimiento y el país tal como se cargaron: verificar siempre contra el artículo.
- Los resultados de la fórmula (VE, RR con IC) se calculan con los eventos; no sirven cuando un grupo tiene 0 eventos (ver C-015) ni cuando el artículo reporta estimaciones por brazo (C-017).

## `Immunogenicity` (`sheetId` 1990986245)

| Cols | Contenido |
|---|---|
| A:K | A ID, B Author year, C Assigned to, D Status, E Asignación, F Actualización, G Title, H DOI, I Type, J Trial name, **K Vaccine** |
| L:T | L NCT, M Trial phase, N Number of participants, O Individuals aged, P Number vaccinated, Q Number placebo, R Country/ies, S Follow-up, T Variant |
| U:V | U Antibody response was measured as, V Unit of measure |
| W:Y | Punto, límite inferior y superior, **vacunados, segunda dosis** |
| Z:AB | Punto, inferior, superior, **placebo, segunda dosis** |
| AC:AE | Punto, inferior, superior, **vacunados, primera dosis** |
| AF:AH | Punto, inferior, superior, **placebo, primera dosis** |
| AI, AJ | Cellular response measured, Main results |
| AK, AL:AO | Adverse events (any) measured as; eventos y totales (intervención, comparación) |
| AP, AQ:AT | Adverse events (serious) measured as; eventos y totales |
| AU:BC | Texto generado por fórmula (diseño, país/seguimiento, resultados): no escribir |

Un ensayo de dosis única va en las columnas de **primera dosis**. Una celda de punto puede traer texto (`Placebo: 464` en lugar del número: revisar).

## Reglas al pasar estas pestañas a `Tablas_capa_1`

Ver `tablas_capa_1.md`, sección "Ensayos". Resumen: Efficacy -> `Clinical efficacy`; eventos adversos de ambas pestañas -> `Safety`; Immunogenicity -> `Immunogenicity`. Si un artículo no reporta anticuerpos, la fila de Immunogenicity queda `Excluded` con nota (el estudio vive en Efficacy).
