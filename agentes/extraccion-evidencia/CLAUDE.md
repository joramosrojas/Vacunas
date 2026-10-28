# Extracción de evidencia de vacunas (contexto del líder)

Las rutas de este archivo son relativas a `agentes/extraccion-evidencia/` salvo que empiecen por `agentes/`.

Proyecto: evidencia de vacunas para el tablero de PAHO (<https://vaccines-pharmacovigilance.paho.org/en>), publicada vía CMS. Este sistema extrae datos de artículos y los pasa a las planillas. Hablar con el usuario en español.

## Antes de empezar cualquier extracción
1. Leer `memoria/correcciones.md` (solo entradas `activa`).
2. Leer **solo** el doc de reglas del tipo en curso en `docs/reglas/` (effectiveness, seguridad_comparativa o seguridad_no_comparativa) más `estados_y_elegibilidad.md` y `producto_vacuna.md`.
3. Planillas e IDs: `schemas/sheets.json`. Mapas de columnas: `docs/planillas/`. No explorar la planilla: ya está documentada. Si cambió, usar `/entender-planilla`.

## Flujo
`/extraer-evidencia` (ver `docs/flujo.md`): fetcher -> extractor (uno por artículo, en paralelo si son 3 o más) -> validar con código -> verifier -> sheet-writer -> reporte. Arquitectura y ahorro de tokens: `docs/arquitectura.md`.

## Reglas que no se negocian
- Listas de validación: valor exacto o vacío (`schemas/lists.json`). Correr `python3 tools/validate_record.py` antes de escribir.
- Escribir por **Episte ID** (columna A), nunca por número de fila recordado. Releer para verificar cada escritura.
- No afirmar un cambio que no se ejecutó y se verificó.
- Sin texto completo no hay `Ok`: `Waiting` con nota de celda en D.
- Producto no nombrado ni inferible, o fuera de la lista: `Excluded` con nota en D y `Vaccine` vacío.
- Destino de las tablas: planilla 2026, pestaña `Tablas_capa_1`, fecha del día en la columna K. Agregar con `append_values`; no borrar nada ajeno.
- No inventar ni calcular IC. Sin IC: "95% CI: Not reported".
- Escribir directo en las filas asignadas (JT por defecto); preguntar solo por criterios nuevos.
- Toda lista de artículos para el usuario lleva el **Episte ID completo** (40 caracteres), fila, autor y año: él busca los PDFs por ID.
- Cuando el usuario corrija algo: `/aprender-correccion`.

## Tokens
No leer artículos completos ni hojas completas en el contexto del líder. Los trabajadores devuelven JSON o tablas cortas. Menos de 3 artículos: extraer en línea, sin subagentes.
