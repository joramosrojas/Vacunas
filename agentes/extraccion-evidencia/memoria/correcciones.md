# Correcciones del usuario

Estados: `activa` (se carga en cada corrida), `promovida` (ya está en `docs/reglas/`), `archivada`.

## C-001 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: escribí texto libre en celdas con lista de selección (unidad "% decline", comparación y unidades inventadas).
- Qué corresponde: usar solo valores de las listas (`schemas/lists.json`); revisar el formato de las filas `Published` antes de escribir.
- Regla: validar con `tools/validate_record.py` antes de escribir. Valor exacto de la lista o vacío.

## C-002 | 2026-10-28 | estado: activa | ámbito: general
- Qué hice: dije que había cambiado el estado de varias filas sin haber ejecutado el cambio.
- Qué corresponde: ejecutar y comprobar releyendo antes de afirmarlo.
- Regla: nunca informar un cambio en planilla sin haberlo releído. El reporte final dice qué se verificó.

## C-003 | 2026-10-28 | estado: activa | ámbito: effectiveness
- Qué hice: excluí los estudios ecológicos de antes y después por no comparar vacunados con no vacunados.
- Qué corresponde: se incluyen; miden cuánto se redujo contraer la enfermedad o la enfermedad grave. La lista de comparación incluye "Pre-vaccination period versus post-vaccination period".
- Regla: los estudios antes/después con reducción de enfermedad o enfermedad grave son elegibles. Unidad `IRR`, punto = % de reducción.

## C-004 | 2026-10-28 | estado: activa | ámbito: effectiveness
- Qué hice: omití los IC y valores de P que el artículo sí reporta (de las tasas o del RR).
- Qué corresponde: incluir en el texto de la tabla las tasas con IC, el RR y la P; si no hay IC del estimador: "95% CI: Not reported".
- Regla: no dejar resultados sin su IC o la frase "Not reported". No inventar ni calcular IC.

## C-005 | 2026-10-28 | estado: activa | ámbito: effectiveness
- Qué hice: dejé en Waiting un artículo con varios resultados por comunidad porque no había una estimación única.
- Qué corresponde: incluirlo con todos los resultados en la misma celda (columna X o AG, líneas separadas).
- Regla: varios grupos/comunidades/temporadas -> una celda multilínea en X (enfermedad) o AG (enfermedad grave).

## C-006 | 2026-10-28 | estado: activa | ámbito: effectiveness
- Qué hice: dejé Ok estudios sin nombre de producto.
- Qué corresponde: si el producto no se nombra y no se puede inferir -> `Excluded`, `Vaccine` vacío y nota de celda en D con la razón. Si no hay texto completo -> `Waiting` con nota.
- Regla: ver `docs/reglas/producto_vacuna.md`. Las notas se escriben en la celda de estado (D).

## C-007 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: ediciones por número de fila recordado; otra persona borró una fila y mis ediciones cayeron una fila más abajo, dejando la tabla desordenada.
- Qué corresponde: relocalizar las filas antes de editar.
- Regla: ubicar por Episte ID o releyendo; verificar tras cada escritura; no borrar filas ajenas.

## C-008 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: pregunté antes de cambiar celdas.
- Qué corresponde: el usuario indicó que no es necesario preguntar para cambiar celdas de las filas asignadas.
- Regla: escribir directo en las filas asignadas; preguntar solo ante criterios nuevos (vacuna nueva, lista nueva, exclusión por criterio).

## C-009 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: dejé la fecha de carga sin poner en `Tablas_capa_1`.
- Qué corresponde: columna K con la fecha del día en formato `28 Octubre 2026`.
- Regla: toda fila nueva en `Tablas_capa_1` lleva la fecha de hoy en K.

## C-010 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: agregué filas en la planilla 2025.
- Qué corresponde: "la segunda planilla" = `[Vacunas_2026] Información regulatoria y tablas de efectos`.
- Regla: destino por defecto = planilla 2026 (`schemas/sheets.json`). Solo escribir en la 2025 si el usuario lo pide.

## C-011 | 2026-10-28 | estado: activa | ámbito: effectiveness
- Qué hice: vacuna "Varivax" en estudios que no la nombran, y país "USA".
- Qué corresponde: país completo en inglés ("United States"); Varivax solo si se nombra o se infiere por país y período (EE. UU. hasta 2006).
- Regla: ver `docs/reglas/producto_vacuna.md` y `lists.json` (`country_fixes`).

## C-012 | 2026-10-28 | estado: activa | ámbito: general
- Qué hice: listé artículos pendientes solo con autor y año.
- Qué corresponde: el usuario busca los PDFs por Episte ID; incluirlo siempre.
- Regla: toda lista de artículos que se entregue al usuario (pendientes, no accesibles, excluidos, reportes) lleva el Episte ID completo de 40 caracteres, además de fila, autor y año.

## C-013 | 2026-10-28 | estado: activa | ámbito: elegibilidad
- Qué hice: extraje datos de artículos que no cumplían criterios (subgrupo embarazadas, solo comparador activo) y de los que iban a quedar excluidos.
- Qué corresponde: aplicar los criterios formales (`docs/reglas/estados_y_elegibilidad.md`); si algo pasó la selección, marcar `Excluded` con nota en D; no extraer datos de los excluidos.
- Regla: decidir elegibilidad antes de extraer; `Excluded` = solo estado + nota.

## C-014 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: usé "Contracting varicella" como Outcome en Clinical efficacy.
- Qué corresponde: Outcome genérico, igual que en Effectiveness.
- Regla: en Tablas_capa_1, Outcome = `Contracting disease` / `Contracting severe disease` para toda enfermedad que no sea COVID (también en Clinical efficacy).

## C-015 | 2026-10-28 | estado: activa | ámbito: effectiveness
- Qué hice: dejé EV/RR sin estimar cuando un grupo tenía 0 eventos (fórmula de la planilla con #NUM!); luego agregué una línea con los casos y la nota de la corrección.
- Qué corresponde: aplicar la corrección de continuidad de RevMan (sumar 0,5 a cada celda del 2x2) y escribir solo EV y RR con su IC, sin nota ni proporción de casos.
- Regla: con cero eventos en un grupo, calcular RR e IC (log RR, error estándar con 0,5 en las 4 celdas) y EV = 1 - RR. En la celda de la tabla poner solo `VE: x% (95% CI: a - b)` y `RR: x (95% CI: a - b)`, sin la nota "0.5 added" ni la proporción de casos. Solo con cero eventos; si no, usar lo que da la planilla o el artículo.

## C-016 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: tomé "varivax" literalmente y dejé fuera SKYVaricella.
- Qué corresponde: "lo de varivax" = toda la vacuna de varicela (Varivax y SKYVaricella), en todas las pestañas (Effectiveness, Efficacy, Immunogenicity, Post_authorization_safety).
- Regla: al pedir una vacuna por nombre, revisar todas las pestañas y las marcas de la misma enfermedad; solo pasan a Tablas_capa_1 las filas `Ok`.

## C-017 | 2026-10-28 | estado: activa | ámbito: general
- Qué hice: pasé a la tabla datos de Varis tal como estaban en la planilla (Varivax, USA, 72 % agrupado, placebo "64") sin contrastarlos con el artículo.
- Qué corresponde: verificar producto, país, seguimiento y población contra el texto antes de pasar a Tablas_capa_1; usar las estimaciones que reporta el artículo por grupo, no agrupar brazos de distinta formulación.
- Regla: con el texto disponible, contrastar producto, país, seguimiento, N analizado y estimaciones por brazo antes de escribir en Tablas_capa_1.
