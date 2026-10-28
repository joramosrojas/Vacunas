---
name: aprender-correccion
description: Registra una corrección del usuario en la memoria del sistema de extracción y, si se repite, la convierte en regla. Úsalo cada vez que el usuario corrija un formato, un criterio, una traducción o una decisión de estado.
---

# Aprender de una corrección

Objetivo: que el mismo error no se repita, gastando pocos tokens.

## Pasos

1. **Redactar la entrada** al final de `memoria/correcciones.md` con este formato (4 líneas, sin relleno):
   ```
   ## C-0NN | AAAA-MM-DD | estado: activa | ámbito: effectiveness|seguridad|traduccion|planillas|general
   - Qué hice: ...
   - Qué corresponde: ...
   - Regla: <instrucción corta en imperativo>
   ```
   Usa el siguiente número libre. Si ya existe una entrada igual, súmale `(repetida YYYY-MM-DD)` en lugar de duplicarla.
2. **Clasificar el destino:**
   - Criterio de extracción o de estado -> también `docs/reglas/<tema>.md` (una línea).
   - Decisión del proyecto (qué se incluye, qué planilla, qué formato) -> `memoria/decisiones.md`.
   - Traducción -> par en `docs/reglas/traduccion_es.md`.
   - Formato de planilla o lista -> `docs/planillas/*.md` y, si es una lista, `schemas/lists.json`.
   - Ejemplo útil -> `memoria/casos_resueltos.md` (como máximo 6 líneas).
3. **Promoción.** Cuando una entrada se repite o ya está copiada a `docs/reglas/`, cambia su estado a `promovida` (se deja de cargar en cada corrida).
4. **Compactar.** Si hay más de 25 entradas `activa`, fusiona las de un mismo ámbito en una sola regla y archiva las demás cambiando su estado a `archivada`.
5. **Confirmar** al usuario en una línea qué se guardó y dónde.

No guardar: datos de artículos concretos (eso vive en la planilla), opiniones sin consecuencia práctica ni nada con credenciales o datos personales.
