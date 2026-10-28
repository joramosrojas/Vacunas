# Reglas de extracción: seguridad post-autorización comparativa

Leer también `docs/planillas/extraccion_post_auth_safety.md`.

## Cuándo es comparativa

El estudio compara la frecuencia de un evento adverso entre vacunados y no vacunados, entre períodos (antes/después, riesgo vs. basal) o con expectativa poblacional (observados/esperados). Casos: cohortes, casos y controles, series de casos autocontroladas (SCCS), estudios de SIR / O/E.

## Registro

- `U` (Comparative study) = `Yes`; `BO` (Non-comparative) = `No`.
- Comparación (K): `Vaccinated versus unvaccinated`, `Pre-vaccination period versus post-vaccination period` o `NA`.
- Hasta **5 desenlaces** por fila. Cada desenlace usa el nombre **de la lista** (evento de especial interés o evento listado). Si el evento no está en la lista, `NA` y describirlo en "measured as"; avisar al líder para valorar ampliar la lista.
- "Outcome was measured as": definición de caso o fuente de ICD usada, corta.
- Medida (lista): `RR`, `OR`, `HR`, `IRR`, `RI`, `Rate ratio`, `SIR`, `ROR`, `OE ratio`, `NA`. Usar la que el artículo reporta; no convertir.
- Primera dosis y segunda dosis en sus columnas; si solo hay un resultado global, va en primera dosis y se indica en el texto.
- Subgrupos (sexo, edad, intervalo de riesgo): una fila de tabla por grupo cuando son de interés; en la planilla de extracción se usa el desenlace más global y el resto va en texto.

## Tabla final

- C = `Comparative`; D = nombre del evento.
- G: `Rate ratio: 1.04% (95% CI: 0.88 - 1.23)` o con dosis (`First dose: ...`, `Second dose: ...`). Mantener la medida tal como la nombra el artículo.
- Producto: si el artículo combina productos y no desglosa, no se incluye en la tabla de una vacuna concreta (`Excluded`, nota).

## Flags

Los mismos de effectiveness más `event_not_in_list`, `observed_expected`, `mixed_products`.
