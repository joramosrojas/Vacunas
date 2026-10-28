# Arquitectura y optimización de tokens

## Decisión

**Pipeline por etapas con un líder (la sesión principal) y trabajadores especializados que corren cada uno en su propio contexto.**
No es un sistema de agentes autónomos abiertos: el flujo es conocido de antemano (leer planilla -> extraer -> verificar -> escribir), así que se usa un *workflow* predefinido con trabajadores en paralelo solo donde hay trabajo independiente (un artículo por trabajador).

## Por qué esta forma (resumen de la investigación)

| Hallazgo | Fuente | Qué hicimos con eso |
|---|---|---|
| Para tareas con pasos conocidos conviene un workflow (encadenado, paralelo, evaluador-optimizador) antes que agentes autónomos; empezar simple | [Anthropic, Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (vía resúmenes: [Spring AI](https://docs.spring.io/spring-ai/reference/api/effective-agents.html)) | Etapas fijas; el verificador es un evaluador independiente |
| Patrón orquestador-trabajadores; un agente líder delega a subagentes en paralelo | [Anthropic, multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | El líder planifica y reparte; trabajadores devuelven solo resultados |
| Los agentes gastan ~4x los tokens de un chat y los sistemas multi-agente ~15x; solo conviene en tareas muy paralelizables | misma fuente | **Regla de umbral**: menos de 3 artículos se extraen en línea, sin subagentes |
| Los skills cargan solo nombre y descripción al inicio y el cuerpo bajo demanda (*progressive disclosure*); `CLAUDE.md` va siempre cargado, así que debe ser corto | [Glosario de Claude Code](https://code.claude.com/docs/en/glossary.md), guías comunitarias: [vantaige](https://vantaige.io/blog/claude-code-subagents-save-context-3-patterns) | `CLAUDE.md` mínimo; reglas por tipo de estudio en archivos aparte que cada trabajador lee solo si le toca |
| Un subagente tiene contexto propio y solo devuelve su mensaje final al padre; los subagentes no pueden crear otros subagentes | misma fuente | El **líder es la sesión principal**; los trabajadores no se llaman entre sí |
| En extracción para revisiones sistemáticas, LLM + verificación humana es lo más fiable; el desacuerdo entre extractores independientes señala qué celdas revisar | [EviSearch (arXiv 2604.14165)](https://arxiv.org/pdf/2604.14165), [validación humana en la extracción (arXiv 2501.11840)](https://www.emergentmind.com/papers/2501.11840), [revisión de dos sistemas multiagente (arXiv 2607.21920)](https://arxiv.org/pdf/2607.21920) | Registro con `confidence` por campo; el verificador revisa solo campos dudosos y el usuario recibe un reporte de celdas marcadas |

Las cifras de esas fuentes son preliminares (preprints y blogs): se usan como guía de diseño, no como garantía.

## Dónde se ahorran tokens

1. **Contexto aislado por artículo.** Cada `extractor` lee un artículo y devuelve un JSON de unos cientos de tokens. El texto completo nunca vuelve al líder.
2. **Conocimiento de la planilla ya documentado.** Columnas, listas de validación y formatos están en `docs/planillas/` y `schemas/`. Nadie vuelve a descargar 700 filas para "entender" la hoja. Si un agente necesita ver la planilla, usa rangos pequeños (ver `skills/entender-planilla`).
3. **Código en vez de LLM para lo mecánico.** `tools/validate_record.py` valida listas y formatos; `tools/render_tablas.py` arma las filas de `Tablas_capa_1` (inglés y español) a partir del registro. El LLM solo escribe campos libres cortos.
4. **Carga progresiva de reglas.** El `extractor` de effectiveness no lee las reglas de seguridad y viceversa.
5. **Modelos por tarea.** `fetcher` y `sheet-writer` (mecánicos) usan un modelo pequeño; `extractor` y `verifier` uno intermedio; el líder (modelo grande) solo decide casos ambiguos y habla con el usuario.
6. **Caché de textos.** Los PDFs se convierten una vez a texto en `work/textos/` (con `pdftotext`) y los trabajadores leen el texto, no el PDF. Los PDFs escaneados se tratan aparte.
7. **Lecturas puntuales de la planilla.** Siempre por rango y por Episte ID (columna A), nunca la hoja completa; así se evita también escribir en la fila equivocada cuando otras personas insertan o borran filas.
8. **Memoria compacta.** `memoria/correcciones.md` se resume cuando crece: las correcciones repetidas se promueven a `docs/reglas/` y se archivan.

## Roles

| Rol | Quién | Modelo sugerido | Entrada | Salida |
|---|---|---|---|---|
| Líder | Sesión principal | grande | pedido del usuario | plan, decisiones, reporte final |
| `fetcher` | subagente | pequeño | filas objetivo + carpeta de Drive | manifiesto (Episte ID -> archivo de texto) |
| `extractor` | subagente, uno por artículo, en paralelo | intermedio | texto + reglas del tipo | registro JSON |
| `verifier` | subagente | intermedio | registro + texto | veredicto y campos a corregir |
| `sheet-writer` | subagente | pequeño | registros validados | filas escritas y releídas |

## Límites conocidos

- Los agentes no pueden leer PDFs de pago ni los bloqueados por el proxy. Si no hay texto completo, la fila queda en Waiting con una nota en la columna D (ver `docs/reglas/estados_y_elegibilidad.md`).
- La traducción al español es del propio modelo; el usuario revisa en las primeras corridas y sus correcciones pasan a `memoria/`.
