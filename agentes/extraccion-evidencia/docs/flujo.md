# Flujo de trabajo

```
 usuario ──pide──> LÍDER ──1──> fetcher ──manifiesto──> LÍDER
                      │
                      ├──2──> extractor x N (paralelo, 1 por artículo) ──registro JSON──> LÍDER
                      │
                      ├──3──> verifier (solo campos dudosos o muestra) ──veredicto──> LÍDER
                      │
                      ├──4──> tools/validate_record.py (código)
                      │
                      └──5──> sheet-writer ──> planilla de extracción ──> Tablas_capa_1 ──> reporte al usuario
```

## Pasos

0. **Preparación.** Leer `CLAUDE.md` y `memoria/correcciones.md` (corto). Identificar el tipo (`effectiveness`, `safety_comparative`, `safety_noncomparative`) y cargar solo el doc de reglas de ese tipo.
1. **Localizar.** `fetcher` lista las filas objetivo por rango (estado `Waiting`/`Pending` y vacuna), busca los PDFs en la carpeta de Drive que indique el usuario y los convierte a texto. Devuelve un manifiesto: `episte_id`, fila, archivo, calidad del texto (completo / solo resumen / ausente).
2. **Decidir cuántos trabajadores.** Menos de 3 artículos: el líder extrae en línea. 3 o más: un `extractor` por artículo, en paralelo, máximo 5 a la vez.
3. **Extraer.** Cada `extractor` devuelve un registro según `schemas/record.schema.json`, con `confidence` y `flags`. Si el texto está incompleto, lo dice y no inventa.
4. **Validar con código.** `tools/validate_record.py` revisa listas, formatos y coherencia. Los errores vuelven al `extractor` una sola vez.
5. **Verificar.** `verifier` compara contra el texto los campos con `confidence` baja o con `flags`, más una muestra del 20 % de los registros restantes. Si discrepa del extractor en un valor numérico, gana el texto; si no está claro, pregunta el líder al usuario.
6. **Escribir.** `sheet-writer` ubica cada fila por Episte ID (columna A), escribe en la planilla de extracción (columnas C:D e I:AM, o las de seguridad), relee y confirma. Luego genera las filas de `Tablas_capa_1` con `tools/render_tablas.py` y las agrega al final de la segunda planilla, con la fecha de hoy en la columna K.
7. **Reportar.** El líder entrega una tabla corta: fila, artículo, estado, valores clave, y lista de celdas marcadas. No pega textos largos.
8. **Aprender.** Si el usuario corrige algo, `/aprender-correccion` lo registra en `memoria/correcciones.md`.

## Puntos de control con el usuario

- Antes de **excluir** una fila por criterio (no por falta de texto): decirlo en el reporte con el motivo; la nota queda en la celda D.
- Antes de agregar una vacuna, lista o columna nueva: preguntar.
- No hace falta preguntar para escribir o corregir celdas de las filas asignadas (instrucción del usuario).

## Qué nunca se hace

- Afirmar un cambio en la planilla que no se ejecutó, o que no se verificó releyendo.
- Escribir texto libre en una celda con lista de validación.
- Borrar filas, columnas o contenido ajeno sin que lo pidan.
- Escribir por número de fila recordado: las filas cambian cuando otras personas editan. Siempre por Episte ID o releyendo antes.
