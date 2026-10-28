# Sistema de agentes: extracción de evidencia

Contexto: el proyecto busca evidencia de varias vacunas y la publica en el tablero de PAHO
(<https://vaccines-pharmacovigilance.paho.org/en>) mediante un CMS. Este sistema hace la parte de **extracción**:

```
artículo (PDF/texto) -> registro estructurado (JSON) -> planilla de extracción -> Tablas_capa_1 (EN + ES)
```

## Qué extrae

| Tipo | Pestaña de extracción | Doc de reglas |
|---|---|---|
| Effectiveness | `Effectiveness` | [`docs/reglas/effectiveness.md`](docs/reglas/effectiveness.md) |
| Seguridad post-autorización comparativa | `Post_authorization_safety` | [`docs/reglas/seguridad_comparativa.md`](docs/reglas/seguridad_comparativa.md) |
| Seguridad post-autorización no comparativa | `Post_authorization_safety` | [`docs/reglas/seguridad_no_comparativa.md`](docs/reglas/seguridad_no_comparativa.md) |

Destino final: pestaña `Tablas_capa_1` de la **segunda planilla** (`[Vacunas_2026] Información regulatoria y tablas de efectos`).

## Cómo se usa

1. Abrir Claude Code dentro de esta carpeta (o desde la raíz; los subagentes y skills están enlazados en `.claude/`).
2. Pedir, por ejemplo: `/extraer-evidencia effectiveness varicela` o "extrae las filas Waiting de Effectiveness para Varivax; los PDFs están en <carpeta de Drive>".
3. Corregir lo que haga mal. Después `/aprender-correccion` convierte la corrección en memoria permanente.

## Mapa de la carpeta

| Ruta | Contenido |
|---|---|
| `CLAUDE.md` | Instrucciones del agente líder (siempre cargadas; corto a propósito) |
| `docs/arquitectura.md` | Decisiones de diseño, fuentes y optimización de tokens |
| `docs/flujo.md` | Pasos del pipeline, qué hace cada agente, puntos de control |
| `docs/planillas/` | Mapa de columnas y formatos de cada planilla (se leen solo cuando hacen falta) |
| `docs/reglas/` | Reglas de extracción por tipo de estudio (se leen solo las del tipo en curso) |
| `schemas/` | IDs de planillas, listas de validación, esquema del registro |
| `tools/` | Scripts deterministas: validar registro y generar filas de `Tablas_capa_1` |
| `agents/` | Subagentes: `fetcher`, `extractor`, `verifier`, `sheet-writer` |
| `skills/` | `extraer-evidencia`, `aprender-correccion`, `entender-planilla` |
| `memoria/` | Correcciones del usuario, decisiones y casos resueltos (aprendizaje continuo) |
| `work/` | Borradores y caché de textos (no se versiona) |
