# Cómo decidir el producto (columna `Vaccine`)

1. Si el artículo **nombra** el producto (en métodos, introducción o resumen), usarlo si está en la lista de `schemas/lists.json`.
2. Si no lo nombra, se puede **inferir** solo si en ese país y período existía un único producto de la lista:
   - Estados Unidos, vacunación contra varicela hasta 2006: solo Varivax (monovalente). Se infiere `Varivax`.
   - Estados Unidos desde 2005-2006 en adelante: también circula ProQuad (MMRV, no está en la lista) y los artículos no separan los productos. **No se infiere** -> `Excluded` con nota.
3. Si el producto nombrado no está en la lista (ej. Varilrix) -> `Excluded`, `Vaccine` vacío, nota con el nombre del producto.
4. Nunca adivinar por el nombre del fabricante que aparece solo en conflictos de interés o bibliografía.
5. Ante duda, preguntar al usuario con la cita del texto.

## VPH (Gardasil)
- `Gardasil 4` = vacuna cuadrivalente (Gardasil, Silgard, 4vHPV, qHPV; tipos 6/11/16/18). `Gardasil 9` = nonavalente (Gardasil 9, Silgard 9, 9vHPV; tipos 6/11/16/18/31/33/45/52/58). Nombre de visualización provisorio: `Gardasil 4 HPV vaccine` / `Gardasil 9 HPV vaccine`.
- Si el artículo dice solo "quadrivalent" o "9-valent" sin marca: se infiere Gardasil 4 / Gardasil 9 cuando el estudio es de un país donde solo estaba autorizado el producto de Merck (EE. UU., Canadá, Australia, Brasil, países nórdicos y europeos, etc.), sin límite de fecha. **No se infiere en India ni China**, donde hay otros productos 4v y 9v (Cervavac, Cecolin 9, Walvax 9): `Excluded` con nota. Marcar `confidence` medium y flag `product_inferred`. (Usuario, 2026-10-28: la regla por fecha era demasiado estricta.)
- Bivalentes (Cervarix, Cecolin, Walrinvax) no están en la lista: `Excluded`. Si el estudio mezcla productos sin separarlos: `Excluded`.

Al añadir una regla por país/período nueva, anotarla aquí y en `memoria/decisiones.md`.
