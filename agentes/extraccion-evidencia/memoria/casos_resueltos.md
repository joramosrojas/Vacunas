# Casos resueltos (ejemplos modelo)

Ejemplos cortos que el `extractor` puede consultar. Los datos completos están en las planillas.

## Effectiveness — varicela (primera corrida, 2026-10-28)

| Episte ID (inicio) | Estudio | Resultado | Por qué |
|---|---|---|---|
| 773fa108 | Galil 2002, brote en guardería | Ok. VE 79 % (66-88) enfermedad; 95 % (84-98) moderada/grave | Nombra Varivax; cohorte con no vacunados; IC en el texto. Fixture: `tools/tests/galil_648.json` |
| 29bd394c | Gould 2009, brote en escuela | Ok. VE 1 dosis 85,4; 2 dosis 89,1; grave 100 % | VE contra tasa histórica de no vacunados: lo dice la tabla |
| 9cc8255c | Baxter 2013, cohorte prospectiva | Ok. VE 90 % sin IC | "95% CI: Not reported"; dos referencias históricas |
| c8495f07 | Staat 2006, Ohio | Ok. IRR 66 (urgencias) y 65 (hospital) | Antes/después; RR 2,9 con IC en el texto de la tabla |
| f9611a52 | Seward 2002, 3 comunidades | Ok. 71 / 84 / 79 % en una celda | Varios resultados -> una celda multilínea (col. X) |
| 94ba53db | Reynolds 2008, VASP | Ok. IRR 76 hospitalización | Incluye OR ajustado de no vacunados en el texto |
| 306e5205, 0c08a304, 0835f899, 9e3f8083 | Leung 2015 x2, Marin 2022 x2 | Excluded | Producto no nombrado; períodos que llegan a 2008-2019 (MMRV) |
| 64fba5a7 | Sheffer 2005, Israel | Excluded | Vacuna Varilrix, fuera de la lista |
| feb9d3c5 | Clements 1999 | Waiting | Solo resumen; nota en D |

## Referencias de formato en la planilla (filas `Published`)

- Antes/después con reducción: fila de Gentile A (Abrysvo): `IRR 34.9 (16.9 - 49.0)`, tabla `Reduction in hospitalization rate:\nIRR: 34.9% (95% CI: 16.9 - 49.0)`.
- VE con IC: Luhm KR (Dengvaxia): VE 17,5 % (12,9-21,9) primera dosis y 24,3 % (20,1-28,2) segunda.
- Seguridad comparativa: Dag Berild J 2022 (BNT162b2, SCCS): evento `Thrombosis with thrombocytopenia syndrome`, medida `Rate ratio`, 1.04 (0.88 - 1.23), comparación pre/post.
- Seguridad no comparativa: Otero-Losada M 2023 (BNT162b2): `The study described a disproportionality analysis of ... using data from Medicines and Healthcare Products Regulatory Agency`; `The study reported Guillain-Barré Syndrome incidence was 1.3 per million doses`.

## Seguridad post-autorización — varicela (prueba, 2026-10-28)

| Episte ID (inicio) | Estudio | Resultado | Por qué |
|---|---|---|---|
| ca8c2d8f | Moro 2022, VAERS 2006-2020 | Ok, no comparativa, Varivax | El artículo separa la vacuna monovalente (VAR) del MMRV; se extrae solo VAR (producto inferido: única monovalente en EE. UU.). `participants_label` = "doses distributed" |
| 3c93de97 | Weinmann 2019, herpes zóster en niños | Excluded, comparativa | No nombra el producto y el período 2003-2014 incluye MMRV. El evento (herpes zóster) no está en la lista de desenlaces: `NA` y descripción en "measured as" |

Aprendido: en seguridad comparativa sin estimador de razón (solo tasas) la planilla no tiene dónde poner el resultado; queda en el registro JSON y, si pasa a Ok, hace falta decidir cómo representarlo.

## Seguridad post-autorización varicela (filas 590-602, lote 2)
- Ok (no comparativa, farmacovigilancia pasiva): Galea 844eaf59055d0f4325d6c12a37ef4086453107b6, Chaves d9785f064d539608aefc797308c1abfda04c3f83, Wise 6b9a83fb96f5d6507e165cc46f662ee0f2392cc4, Moro ca8c2d8f7693e3a4b1b1255252bcc5c1b242cb49, Sharrar 9659e8eace5b6b27e567a1822e54f6fd176a13f5, Goulleret 371725e1dc0f58e823ee07c7aedd2a8155727082.
- Excluded: Willis 4917825de9f606ddbf753fb150655bbae52baa88 (embarazadas), Klein 76cc7af0edf25bc707f8bdce592f108eb7c97345 (solo comparador activo), Liu 057732d07d6325cafe4a88c86ee940ddc4b72b9d (producto), Weinmann 6c5f193f6cf2557525859ce7f83b66dc2e34fa8e / 7038eaf0add74c8ca56c90e62d8552390105a5fb / 3c93de97d81cd49203708559e046e61877532f57.
- Países: Galea "Worldwide", Goulleret "Europe"; Sharrar "United States" inferido; Galea tiene 55,7 M dosis en Resultados vs "155 million" en Discusión (se usó 55,7 M).
