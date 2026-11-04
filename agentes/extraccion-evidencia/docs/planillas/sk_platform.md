# Destino en SK Platform (síntesis de vacunas)

Las tablas de `Tablas_capa_1` se publican en la síntesis de cada vacuna en SK Platform (`https://www.skplatform.org/app/syntheses/<UUID>/work`, paso *Report*). Una síntesis por vacuna **e idioma** (la versión en español es otra síntesis). Herramienta: `tools/sk_upload.py`; procedimiento: `skills/subir-a-sk/SKILL.md`. Verificado el 2026-10-28 con Vimkunya, Varivax, SKYVaricella y Gardasil 4.

## Cómo se guarda

- Cada sección del *Report* es una fila de `reports.synthesis_reports` (`synthesis_id`, `section_id`, `content`). `content` es un documento TipTap (`doc` > `heading` / `paragraph` / `table`).
- Las citas son nodos `reference` con el **Episte ID** (40 caracteres). Para que se resuelvan, el ID debe existir en `sk_synthesis_references` de **esa** síntesis (`type: references_manager_epistemonikos`, `source: epistemonikos`, `type_identifier` = ID). Una síntesis nueva trae 0 referencias.
- API: `POST https://api.skplatform.org/v1/graphql` (Hasura) con `Authorization: Bearer <valor de la cookie sk:token>`. Mutaciones usadas: `insert_reports_synthesis_reports`, `update_reports_synthesis_reports_by_pk` (variable `json!`, no `jsonb!`), `insert_sk_synthesis_references`.
- Las secciones de efectos no existen hasta que se crean: la síntesis nueva solo trae las 8 de información general.

## Secciones (el ID cambia por idioma; la herramienta las busca por nombre)

| Clave | Inglés | Español |
|---|---|---|
| `efficacy` | Vaccine efficacy and effectiveness | Eficacia y efectividad de la vacuna |
| `safety` | Vaccine safety | Seguridad de la vacuna |
| `post` | Post-authorization safety | Seguridad post-autorización |
| `trials` | General characteristics of clinical trials | Características generales de los ensayos clínicos |

No se tocan: Authorization/prequalification, Manufacturer, General characteristics, Dosing and schedule, Indications and contraindications, Precautions, Storage and logistics, Monitoring.

## Contenido de cada sección

**`efficacy`**: `Vaccine efficacy` (tabla *Immunogenicity* con filas Antibody response y Cellular response; tabla *Efficacy*), `Vaccine efficacy in subgroups`, `Vaccine effectiveness` (*Effectiveness ... (comparative studies)*).
**`safety`**: tabla *Safety* y tabla *Safety ... by subgroup of interest*.
**`post`**: `Comparative studies` (columnas Outcome = evento; Study design; Country...; Main results) y `Non-comparative studies` (columnas Reference | Study description and main results; la cita y el texto de la columna F).
**`trials`**: `Phase N` > `Trial name`, `Registry ID` (enlace a ClinicalTrials.gov para NCT), `Available publications` (citas).

Títulos: `<Tipo> of the <Vacuna>`; en español `<Tipo> de la vacuna <Marca> contra <enfermedad>` (p. ej. `Seguridad de la vacuna Varivax contra varicela`). Primera columna y etiquetas (`VE:`, `Vaccine group`) en negrita; `Vaccine group`/`Placebo group` subrayadas.

## Qué tabla recibe cada fila de `Tablas_capa_1`

| Sección (B) | Grupo (D) | Tabla en SK |
|---|---|---|
| Immunogenicity | Overall | Immunogenicity |
| Clinical efficacy | Overall | Efficacy |
| Clinical efficacy | otro grupo | Efficacy by subgroup of interest |
| Effectiveness | cualquiera | Effectiveness (comparative studies) |
| Safety | Overall / otro | Safety / Safety by subgroup |
| Post-authorization safety | `Comparative` / `Non-comparative` (C) | Comparative / Non-comparative |

- **ECA vs placebo en niños = tabla general** (C-024). Si la planilla tiene la fila con grupo `Children and adolescents`, debe existir también la fila `Overall` (se decidió dejar ambas: aparece en general y en subgrupos).
- Filas `Booster` y `Country reports` no tienen tabla en SK; la herramienta las omite y avisa.
- Sin filas en una sección: **tabla estándar de "no hay estudios"** (mensajes en `tools/sk_upload.py`, `LANG`). Con la vacuna sin ninguna fila (p. ej. SKYVaricella) se usa `--allow-empty`.
- **Cada síntesis es de un producto.** `Gardasil 4 HPV vaccine` va a la síntesis cuadrivalente; `Gardasil 9 HPV vaccine`, a la suya. No mezclar.

## Español

Misma estructura con las columnas H:J. Títulos y mensajes tomados de las síntesis de referencia en español (Ixchiq, MMR L-Zagreb, LC16m8): `Desenlace`, `Principales resultados`, `Eficacia*`, `Estudios comparativos`, `No se identificaron estudios que reporten la eficacia de la vacuna.`, `Contraer la enfermedad` / `Contraer la enfermedad severa`, `Niños y adolescentes`. El nombre en los títulos lo da `--name`.

## Ensayos (`trials`)

Nombre = primera línea de la columna E; fase = `Phase N` en E (si falta, `Phase not reported`); publicaciones = Episte IDs de las filas del ensayo. **El NCT no siempre está en `Tablas_capa_1`** (en Vimkunya la columna E trae autor y año): sacarlo de las pestañas `Efficacy`/`Immunogenicity` de la planilla de extracción (columna NCT) y pasarlo con `--trials`. Ensayos sin artículo con resultados (registros `Excluded`) no se listan.

## Riesgos

- El token es la sesión del usuario: no guardarlo en archivos ni commits; se pasa por `SK_TOKEN` en cada sesión y expira.
- Otras personas editan la síntesis en paralelo: la herramienta no sobrescribe reportes existentes sin `--replace`, y `--only` limita el reemplazo a una sección.
- Un reporte sobrescrito no se recupera desde aquí (SK guarda historial de versiones: *Version history* en la pantalla).
