---
name: subir-a-sk
description: Sube a la síntesis de una vacuna en SK Platform las tablas de efectos (eficacia, efectividad, seguridad, seguridad post-autorización y características de ensayos) desde Tablas_capa_1, en inglés o español. Úsalo cuando el usuario pida subir o actualizar tablas en SK o pase el enlace de una síntesis.
---

# Subir tablas de una vacuna a SK Platform

Todo el formato y las reglas están en `docs/planillas/sk_platform.md`; léelo antes de la primera subida de la sesión. La herramienta es `tools/sk_upload.py` (`build` -> `upload`). Hablar con el usuario en español.

## Antes de empezar

1. **Enlace de la síntesis** (URL o UUID) y su idioma. Nombre en el título de cada síntesis (`inspect`); si el usuario manda varios enlaces, identifica cuál es de qué vacuna e idioma por el nombre, no por el orden. Las síntesis "de referencia" que pase son modelos, no destinos.
2. **Token.** Pídele al usuario el valor de la cookie `sk:token` (sesión abierta en skplatform.org) y exporta `SK_TOKEN` solo en el comando que lo usa. No lo escribas en archivos, commits ni mensajes. Si expiró, pide otro.
3. **Qué hay ya en la síntesis**: `python3 tools/sk_upload.py inspect <URL>`. Si ya tiene reportes de efectos, pregunta antes de reemplazar.

## Pasos

1. **Leer las filas** de la vacuna en `Tablas_capa_1` (columna A = nombre de visualización, `schemas/lists.json` `vaccine_display`). Ubica el rango leyendo solo A:B por tramos y luego `A:K` de ese rango (nunca la pestaña entera). Guarda las filas como JSON (lista de listas) en `work/rows_<vacuna>.json`.
   - Para español, las columnas H:J deben estar llenas.
   - Verifica que las filas sean de **esa** vacuna: Gardasil 4 y Gardasil 9, Varivax y SKYVaricella van en síntesis distintas.
2. **Ensayos.** Si hay filas de Clinical efficacy / Safety / Immunogenicity, falta el NCT y la fase: léelos de `Efficacy`/`Immunogenicity` (planilla de extracción) y arma `work/trials_<vacuna>.json` = `[{"phase":"3","name":"...","registry":"NCT...","refs":["<Episte ID>"]}]`. Si no hay ensayos, no hace falta.
3. **Construir**: `python3 tools/sk_upload.py build --rows work/rows_<v>.json --vaccine "<nombre en A>" --lang en --out work/sk_<v>_en.json [--trials ...] [--preview]`. En español agrega `--lang es --name "<Marca> contra <enfermedad>"`. Vacuna sin filas: `--allow-empty`. Lee los `AVISO`.
4. **Probar**: `upload ... --dry-run` y revisa qué crea o reemplaza.
5. **Subir**: `SK_TOKEN=... python3 tools/sk_upload.py upload --docs work/sk_<v>_<lang>.json --synthesis <URL>` (añade `--replace` y/o `--only efficacy,safety` solo si el usuario lo aprobó). La herramienta registra las referencias que faltan, crea los reportes y **relee para verificar** tablas y citas; si dice `ERROR`, no des la carga por buena.
6. **Mirar el resultado** (opcional, recomendable la primera vez): abre la síntesis con Playwright y la cookie, pestañas de las cuatro secciones, y revisa que las citas salgan numeradas y no `[?]`.
7. **Reportar** en una tabla corta: síntesis, idioma, secciones, filas por tabla, referencias nuevas, filas omitidas y por qué (otra vacuna, Booster...), y lo que quedó con tabla estándar.

## Reglas

- No sobrescribir reportes existentes sin aprobación; no tocar secciones de información general.
- Una fila de `Tablas_capa_1` que no esté en SK, o al revés, se reporta; no se corrige en silencio.
- Lo que el usuario corrija del formato: `/aprender-correccion` y actualizar `docs/planillas/sk_platform.md` y los textos de `LANG` en la herramienta.
- Tras cambiar `tools/sk_upload.py`: `python3 -I -m unittest discover -s tools/tests`.
