# Cómo decidir el producto (columna `Vaccine`)

1. Si el artículo **nombra** el producto (en métodos, introducción o resumen), usarlo si está en la lista de `schemas/lists.json`.
2. Si no lo nombra, se puede **inferir** solo si en ese país y período existía un único producto de la lista:
   - Estados Unidos, vacunación contra varicela hasta 2006: solo Varivax (monovalente). Se infiere `Varivax`.
   - Estados Unidos desde 2005-2006 en adelante: también circula ProQuad (MMRV, no está en la lista) y los artículos no separan los productos. **No se infiere** -> `Excluded` con nota.
3. Si el producto nombrado no está en la lista (ej. Varilrix) -> `Excluded`, `Vaccine` vacío, nota con el nombre del producto.
4. Nunca adivinar por el nombre del fabricante que aparece solo en conflictos de interés o bibliografía.
5. Ante duda, preguntar al usuario con la cita del texto.

Al añadir una regla por país/período nueva, anotarla aquí y en `memoria/decisiones.md`.
