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

## C-018 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: separé en dos filas de Tablas_capa_1 los subgrupos por edad (60-74 y 75 o más) del mismo estudio y desenlace.
- Qué corresponde: una sola fila, con grupo `Older adults`, y en las celdas de participantes (E, H) y resultados (G, J) un bloque por subgrupo de edad.
- Regla: en Tablas_capa_1, una fila por estudio, desenlace y grupo. Los subgrupos por edad van juntos en `Older adults`, con un bloque por rango de edad en E, G, H y J.

## C-019 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: agregué dos filas con el mismo Outcome y grupo para desenlaces solapados del mismo estudio (hospitalización por enfermedad respiratoria, primaria, y por enfermedad respiratoria baja, secundaria).
- Qué corresponde: dejar solo el análisis principal.
- Regla: si dos desenlaces del mismo estudio caen en el mismo Outcome y grupo, dejar solo el del análisis principal (desenlace primario).

## C-020 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: dejé en Tablas_capa_1 filas que citaban el preprint de un estudio ya publicado.
- Qué corresponde: reemplazar el preprint por el artículo de revista (misma cita y Episte ID del artículo publicado) y dejar el preprint con estado `Preprint`.
- Regla: si hay versión publicada, la tabla cita la revista; la fila del preprint pasa a `Preprint`.

## C-021 | 2026-10-28 | estado: activa | ámbito: planillas
- Qué hice: el sheet-writer leyó los IDs de unas filas y escribió después por número de fila; mientras tanto otras personas borraron e insertaron filas y se sobrescribieron 5 filas ajenas de Post_authorization_safety (Donahue, Rodríguez-Galán, Souayah, Bukowinski, Lipkind). Antes, un append_values sobre la última fila existente de la hoja sobrescribió A:D de esa fila (Lee LE, Goulleret), que se restauró a mano.
- Qué corresponde: las planillas se editan en paralelo; nunca escribir por una fila leída hace minutos.
- Regla: releer A (Episte ID) de la fila destino inmediatamente antes de cada escritura y escribir solo una fila por llamada; no usar `append_values` con un rango que apunte a una fila con datos (escribe en esa fila); tras cada escritura releer. Si el ID no coincide, no escribir. Antes de sobrescribir cualquier celda con datos, leer su contenido.

## C-022 | 2026-11-03 | estado: activa | ámbito: effectiveness
- Qué hice: dejé un solo valor en X–Z (p. ej. Fairley: solo mujeres <28 años; Schlecht: solo el desenlace cervical) cuando el artículo reportaba varios grupos etarios o dos desenlaces del mismo bloque (enfermedad o enfermedad grave).
- Qué corresponde: enfermedad y enfermedad grave van siempre en celdas distintas (X y AG). La celda multilínea se usa solo cuando hay más de un desenlace o grupo dentro de la enfermedad (X) o más de uno dentro de la enfermedad grave (AG); nunca se mezclan enfermedad y enfermedad grave en una misma celda. Sin valores en Y/Z (ni en AA–AD) en ese bloque. Misma lógica de C-005. Si el artículo reporta una estimación global, va solo esa (en las columnas numéricas) y no se agregan subgrupos (edad, dosis, genotipo); los subgrupos solo se listan cuando no hay global.
- Regla: formato `<Desenlace o grupo>:\n<medida>: <punto> (95% CI: lo – hi)`, con línea en blanco entre desenlaces; para grupos por edad, una línea por grupo (`16 to 17 years: -45.3% (95% CI: ...)`); si hay estimación global, va primera (`All women ...`). Sin salto de línea inicial, con el mismo formato de % en todas las líneas. No incluir controles negativos (p. ej. herpes genital en Fairley) ni grupos que no son de la población vacunada de interés. Las columnas de N (O/Q) se aclaran en "measured as" (V) si corresponden a un subgrupo. Tablas_capa_1 (G/J) lleva los mismos bloques. Extensión de C-005 y C-019: el desenlace primario va en columnas numéricas solo si hay un único resultado; con varios, todo va en X/AG.

## C-023 | 2026-11-04 | estado: activa | ámbito: seguridad
- Qué hice: guardé "NA" como desenlace cuando el evento no estaba en `safety_outcomes`; el validador lo aceptó y Tablas copió "NA".
- Qué corresponde: si el evento no está en la lista, agregarlo a `schemas/lists.json` (textual, sin reformatear con json.dump) y usar su nombre; nunca "NA" como desenlace en seguridad comparativa.
- Regla: no escribir "NA" como evento; ampliar la lista, completar `event_es` y `population_en`/`es.population` si el texto de participantes sale roto, y revisar D de Tablas tras escribir.
