# Memoria del sistema

El sistema aprende de las correcciones del usuario. Tres archivos, de más a menos cargado:

| Archivo | Qué guarda | Cuándo se lee |
|---|---|---|
| `correcciones.md` | Correcciones puntuales del usuario (qué hice, qué corresponde, regla). Solo las `activa` se cargan | Al iniciar cada extracción |
| `decisiones.md` | Decisiones del proyecto que cambian qué se incluye o dónde se escribe | Cuando hay duda de criterio |
| `casos_resueltos.md` | Ejemplos modelo cortos (few-shot) por tipo | El `extractor` del mismo tipo |

Cómo se actualiza: `/aprender-correccion` (ver `skills/aprender-correccion/SKILL.md`). Las correcciones repetidas se copian a `docs/reglas/` y pasan a `promovida`. Las entradas viejas se `archivada`n para que la memoria no crezca sin control.

Nada de datos personales ni credenciales aquí. Los datos de artículos viven en las planillas.
