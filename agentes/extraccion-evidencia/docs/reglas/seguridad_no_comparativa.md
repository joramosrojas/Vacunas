# Reglas de extracción: seguridad post-autorización no comparativa

Leer también `docs/planillas/extraccion_post_auth_safety.md`.

## Cuándo es no comparativa

Describe eventos tras la vacunación sin grupo de comparación: farmacovigilancia pasiva (VAERS, EudraVigilance, Yellow Card, bases nacionales), análisis de desproporcionalidad, series de eventos, cohortes de seguimiento sin control. **Se incluyen** estudios basados en registros de farmacovigilancia pasiva. **Se excluyen** reportes de casos y series de casos individuales.

## Registro

- `U` = `No`; `BO` = `Yes`. K = `NA`; P = `NA`; N = `Cases`, `Vaccinated` o `Doses administered` según lo que cuente el número.
- Participantes (L): número o texto breve del artículo ("11.2 million"); edad: como en el artículo o `NR`.
- **BP** "The study described ...": una frase en minúscula, sin repetir "The study described": qué se analizó, período y fuente. Ejemplo: `a disproportionality analysis of neurological and psychiatric adverse events following immunization during December 9, 2020 to June 30, 2021, using data from Medicines and Healthcare Products Regulatory Agency`.
- **BQ** "The study reported ...": resultados con números tal como los da el artículo: incidencias, proporciones, tasas por millón de dosis. Una línea por hallazgo. Sin interpretación.
- Los bloques de desenlace comparativo (V:BN) quedan vacíos.

## Tabla final

- C = `Non-comparative`; D = `Overall`.
- E = `[Autor, año]\n\n[Episte ID]`.
- F = `<N> participants\n\nNon-comparative study\n<País>\n\nThe study described <BP>\n\nThe study reported <BQ>`.
- G = `NA` y J = `N / A`.
- Español (H, I): traducción de E y F.

## Cuidados

- No sumar ni promediar entre productos si el artículo los reporta juntos: extraer solo lo de la vacuna de interés, o `Excluded` con nota.
- Distinguir "reportes" (notificaciones) de "casos confirmados". Usar el verbo del artículo.
- No convertir tasas de reporte en incidencia ni al revés.
