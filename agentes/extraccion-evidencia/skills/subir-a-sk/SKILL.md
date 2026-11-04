---
name: subir-a-sk
description: Sube a la síntesis de una vacuna en SK Platform las tablas de efectos (eficacia, efectividad, seguridad, seguridad post-autorización y características de ensayos) desde Tablas_capa_1, en inglés o español, y las va actualizando agregando solo los estudios nuevos. Úsalo cuando el usuario pida subir o actualizar tablas en SK o pase el enlace de una síntesis.
---

# Subir y actualizar tablas de una vacuna en SK Platform

Formato y reglas: `docs/planillas/sk_platform.md` (léelo antes de la primera subida de la sesión). Herramienta: `tools/sk_upload.py`. Hablar con el usuario en español.

**Principio: solo se agrega.** Las síntesis tienen contenido subido antes de este sistema que no está en `Tablas_capa_1` ni en la planilla de extracción. Nunca se borra ni se reemplaza; cada vez se agregan los estudios nuevos y se revisan los IDs duplicados.

## Antes de empezar

1. **Enlace de la síntesis** (URL o UUID) y su idioma. Confirma vacuna e idioma por el **nombre** de la síntesis (`inspect`), no por el orden en que llegan los enlaces. Las síntesis "de referencia" que pase el usuario son modelos, no destinos. Cada síntesis es de un producto (Gardasil 4 y 9, Varivax y SKYVaricella van aparte).
2. **Token.** Pídele el valor de la cookie `sk:token` (sesión abierta en skplatform.org) y úsalo solo como `SK_TOKEN=... python3 ...`. No lo escribas en archivos, commits ni mensajes. Si expiró, pide otro.
3. **Estado actual**: `python3 tools/sk_upload.py check <URL>` (solo lectura): IDs duplicados, citas rotas, referencias sin citar. Lo que ya venga mal no se corrige solo: se reporta.

## Pasos

1. **Leer las filas de la vacuna** en `Tablas_capa_1` (columna A = nombre de visualización, `schemas/lists.json` `vaccine_display`).
   - Ubica el rango leyendo solo A:B (o K, la fecha) por tramos; nunca la pestaña entera.
   - Para **actualizar** basta leer las filas nuevas (fecha de la columna K posterior a la última subida, o las últimas de la vacuna): `sync` descarta lo que ya está por Episte ID, así que incluir filas de más no duplica nada.
   - Una lectura grande de `get_values` queda **guardada en un archivo** (`.../tool-results/*.txt`, JSON `{range, values}`): procésala con Python (`json.load`) y guarda la lista de filas en `work/rows_<vacuna>.json`. No transcribas filas a mano.
   - Español: las columnas H:J deben estar llenas.
2. **Ensayos.** Si hay filas de Clinical efficacy / Safety / Immunogenicity falta el NCT: léelo de `Efficacy`/`Immunogenicity` (planilla de extracción) y arma `work/trials_<vacuna>.json` = `[{"phase":"3","name":"...","registry":"NCT...","refs":["<Episte ID>"]}]`. Sin ensayos, no hace falta.
3. **Simular**: `python3 tools/sk_upload.py sync --rows work/rows_<v>.json --vaccine "<nombre en A>" --synthesis <URL> [--lang es --name "<Marca> contra <enfermedad>"] [--trials ...] --dry-run`. Lee el informe: `+` se agrega, `=` ya estaba, `?` **para revisar** (el estudio ya está en la tabla con una etiqueta que no se puede comparar; no se agrega salvo `--include-flagged`), `AVISO` (fila repetida en la planilla, ensayo sin NCT...). Muéstrale al usuario el resumen si hay `?` o algo inesperado.
4. **Escribir**: el mismo comando sin `--dry-run`. La herramienta deja copia de lo que había en `work/backups/`, registra solo las referencias que faltan, agrega las filas (reemplaza únicamente la fila de «no hay estudios» de una tabla a la que llega un estudio), no pisa ediciones simultáneas (si alguien editó la sección mientras tanto, la deja sin tocar y avisa) y **relee para verificar**: ninguna cita anterior perdida, tablas íntegras, sin IDs duplicados. Si dice `ERROR` o `CONFLICTO`, no des la carga por buena.
5. **Revisar**: `check <URL>` otra vez (debe quedar «Sin problemas»); una segunda corrida de `sync` debe decir «Nada nuevo». La primera vez, mira la síntesis con Playwright y la cookie (citas numeradas, no `[?]`).
6. **Marcar `Published` en la planilla de extracción** (solo lo que se subió, y solo si el usuario lo pide o ya lo pidió para esa vacuna): por Episte ID **y** vacuna, en la pestaña de donde salió cada estudio (Effectiveness, Post_authorization_safety, Efficacy, Immunogenicity). Solo cambian las filas en `Ok`; las que estén en otro estado (`Revisado`, `Waiting`...) no se tocan y se informan. **La lista de la pestaña `Efficacy` usa `Publicado`** (la validación es estricta y no acepta `Published`). Regla C-024/C-021: releer el ID de la fila justo antes de cada escritura, una celda por llamada, y al final comparar la pestaña completa antes/después (debe haber cambiado solo esa columna en esas filas).
7. **Reportar** en una tabla corta: síntesis, idioma, filas agregadas por tabla, ya estaban, referencias nuevas, filas «para revisar» y avisos.

Síntesis **vacía** (sin secciones de efectos) o vacuna sin filas: `sync` crea las secciones completas (con tablas estándar de «no hay estudios»); una vacuna sin ninguna fila exige `--allow-empty`. `upload` (build + upload) sigue disponible para cargar documentos ya armados; `--replace` solo si el usuario pide reemplazar.

## Reglas

- No sobrescribir ni borrar contenido existente; no tocar secciones de información general.
- Una fila de `Tablas_capa_1` que no está en SK, o al revés, se reporta; no se corrige en silencio. Texto raro en la planilla (p. ej. «event not in list») se avisa al usuario: se arregla en la planilla y se vuelve a sincronizar (la herramienta no reescribe filas ya subidas: avisa y se corrige a mano en SK si hace falta).
- Lo que el usuario corrija del formato: `/aprender-correccion` y actualizar `docs/planillas/sk_platform.md` y los textos de `LANG` en la herramienta.
- Tras cambiar `tools/sk_upload.py` o `tools/sk_merge.py`: `python3 -I -m unittest discover -s tools/tests`.
