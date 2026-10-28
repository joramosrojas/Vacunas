# Decisiones del proyecto

| Fecha | Decisión | Quién | Dónde aplica |
|---|---|---|---|
| 2026-10-28 | Estudios antes/después (impacto del programa) que miden reducción de enfermedad o enfermedad grave se **incluyen** en effectiveness | usuario | `docs/reglas/estados_y_elegibilidad.md` |
| 2026-10-28 | Producto no nombrado y no inferible -> `Excluded` (sin Vaccine), con nota en D | usuario | `docs/reglas/producto_vacuna.md` |
| 2026-10-28 | Varilrix (Oka-RIT, GSK) no está en la lista de vacunas: `Excluded` con nota (hasta que el usuario amplíe la lista) | usuario (confirmado con Varis 1996) | idem |
| 2026-10-28 | Varicela: nombre de visualización en tablas `Varivax varicella vaccine` | agente, pendiente de confirmar | `schemas/lists.json` |
| 2026-10-28 | Destino de tablas = planilla 2026 (`1c3AlX5q...`), pestaña `Tablas_capa_1`; fecha en K | usuario | `docs/planillas/tablas_capa_1.md` |
| 2026-10-28 | Asignado por defecto: `JT` | usuario | extracciones de varicela |
| 2026-10-28 | Sin texto completo -> `Waiting` + nota en D | usuario | `docs/reglas/estados_y_elegibilidad.md` |
| 2026-10-28 | VE contra no vacunado histórico (Gould, Baxter): se acepta como `Ok` y la tabla aclara el comparador | agente, pendiente de confirmar | `docs/reglas/effectiveness.md` |
| 2026-10-28 | Se agregan `Gardasil 4` y `Gardasil 9` a la lista de vacunas; nombres de visualización provisorios `Gardasil 4/9 HPV vaccine` | usuario (lista) / agente (nombre, pendiente de confirmar) | `schemas/lists.json`, `docs/reglas/producto_vacuna.md` |
| 2026-10-28 | VPH: inferir Gardasil 4/9 por país (no por fecha); no inferir en India ni China. Basu 2019 (India) queda `Excluded` | usuario | `docs/reglas/producto_vacuna.md` |
| 2026-10-28 | Comparador histórico (cohortes vs incidencia histórica) se acepta como `Ok` (Thamsborg, Kjaer, Lynge) | usuario | `docs/reglas/effectiveness.md` |

Resultado de la primera corrida (varicela, 16 filas, Effectiveness): 10 Ok, 5 Excluded, 1 Waiting (ver `casos_resueltos.md`).

## 2026-10-28 | Criterios formales de elegibilidad
Adoptados los criterios del usuario (vacuna, población, comparador, categorías, booster) en `docs/reglas/estados_y_elegibilidad.md`. Seguridad no comparativa solo si es farmacovigilancia pasiva. Excluidos: solo estado + nota.

## 2026-10-28 | Varicela en Tablas_capa_1 (efficacy, immunogenicity, seguridad)
Weibel 1984 (SF, Ok) en Clinical efficacy, Safety e Immunogenicity; Romera-Guirado en Effectiveness. Un dato duplicado entre Efficacy e Immunogenicity (AE de Weibel) se agrega una sola vez. Año de Varis (1996) inferido del DOI; Romera sin año (la planilla no lo trae). SKYVaricella: las 7 filas están `Excluded`, no se agregan.

Varis 1996 (`d0d555eb291aa124b4c32a1c5517453cefaa38d8`): vacuna Oka-RIT de SmithKline Beecham (Varilrix), ensayo en Finlandia -> `Excluded` en Efficacy e Immunogenicity con nota para SF; sus filas se quitaron de `Tablas_capa_1`. Antes de aceptar una fila de varicela, comprobar en el texto quién fabrica la vacuna (Merck = Varivax) y el país: la planilla de extracción traía Varivax y USA por error.

## 2026-10-28 | Vimkunya y Abrysvo en Tablas_capa_1
Nombre de visualización de Vimkunya: `Vimkunya chikungunya vaccine` (confirmado por el usuario). Seguridad de los ensayos (eventos adversos de las pestañas Efficacy e Immunogenicity) va en la sección `Safety`; sin RR en la planilla se escriben las proporciones. Bavarian Nordic: los registros de ensayo (sin artículo con resultados) quedan `Excluded`. Lassen 2026 (DAN-RSV, Abrysvo): sin datos de inmunogenicidad, la fila de Immunogenicity queda `Excluded`; en la tabla, desenlace primario como `Contracting severe disease` y el análisis por edad en una fila `Older adults`.
