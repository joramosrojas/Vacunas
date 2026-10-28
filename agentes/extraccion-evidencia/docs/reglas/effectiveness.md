# Reglas de extracción: effectiveness

Leer también `docs/planillas/extraccion_effectiveness.md` (columnas y listas) y `producto_vacuna.md`.

## Qué extraer, por orden

1. **Elegibilidad y producto** (ver `estados_y_elegibilidad.md`).
2. **Diseño** (`Study design`): como lo llaman los autores, en minúscula inicial, con el adjetivo que lo distingue ("test-negative case-control study", "outbreak investigation cohort study", "ecological before-and-after study").
3. **Comparación** (lista): `Vaccinated versus unvaccinated` o `Pre-vaccination period versus post-vaccination period`. Los estudios que comparan 1 dosis contra 2 dosis **no** son efectividad contra no vacunados: solo se extrae lo que sí compare contra no vacunados o contra un no vacunado histórico.
4. **Participantes** (L): número simple del análisis. Si el artículo da varios, el que entra al cálculo del estimador; si es un estudio ecológico sin N, el número de eventos más informativo o vacío.
5. **Grupos** (N:Q): unidades de la lista. Casos y controles: `Cases`/`Controls`. Cohortes: `Vaccinated`/`Unvaccinated`. Antes/después con conteos anuales: `Cases` (posterior) y `Controls` (previo). Sin conteos: dejar los números vacíos y la unidad de control `NA`.
6. **País, fuente, período** (R:T): país completo en inglés, fuente corta, período con fechas completas si existen.
7. **Variante** (U): solo si el artículo la reporta.
8. **Enfermedad** (V:AD) y **enfermedad grave** (AE:AM): ver abajo.

## Enfermedad vs enfermedad grave

| Desenlace del artículo | Columnas |
|---|---|
| Infección, casos de varicela/COVID, tasa de ataque, consultas ambulatorias o de urgencias | Enfermedad (V:AD) |
| Hospitalización, UCI, muerte/mortalidad, enfermedad moderada o grave por definición del estudio | Enfermedad grave (AE:AM) |

Si el artículo reporta ambos, se llenan los dos bloques. Una definición de "grave" propia del estudio ("más de 250 lesiones") se escribe tal cual.

## Estimadores

- Unidad (lista): `VE`, `RR`, `OR`, `IRR`, `HR`.
- Estudios antes/después con porcentaje de reducción: unidad `IRR`, punto = % de reducción (precedente: fila de Gentile). Límites vacíos si el artículo no da IC del porcentaje.
- No calcular ni inventar IC. No transformar un RR en reducción salvo que el artículo lo haga.
- Un solo estimador en las columnas de dosis correspondientes; varios grupos/comunidades/temporadas -> una celda con líneas en X o AG (ver doc de la planilla).
- Si el artículo da las tasas con IC y un valor de P, **van en el texto de la tabla final**, no en las columnas numéricas.
- VE contra un no vacunado histórico (no concurrente): se extrae, y la tabla final lo aclara en la frase de definición. El líder decide si queda `Ok` o `Waiting`.

## Qué marcar con `flags`

`no_full_text`, `no_ci`, `product_inferred`, `product_unknown`, `historical_control`, `multiple_estimates`, `unit_unclear`, `translation_doubt`.
