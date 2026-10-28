# Agentes del proyecto Vacunas

Cada subcarpeta es un sistema de agentes independiente, con su propio contexto, reglas y memoria.

| Carpeta | Para qué sirve | Estado |
|---|---|---|
| [`extraccion-evidencia/`](extraccion-evidencia/README.md) | Extraer datos de artículos (effectiveness y seguridad post-autorización, comparativa y no comparativa) y pasarlos a la planilla de extracción y a `Tablas_capa_1` | Activo |
| `tablero/` (futuro) | Subir los datos al tablero / CMS de PAHO | Pendiente |

Regla general: ningún agente comparte memoria con otro. Lo que sea común (IDs de planillas, listas de validación) vive en `schemas/` de cada sistema.
