# Vacunas

Proyecto de evidencia de vacunas para el tablero de PAHO (<https://vaccines-pharmacovigilance.paho.org/en>).

## Agentes

Los sistemas de agentes viven en [`agentes/`](agentes/README.md). El primero, [`agentes/extraccion-evidencia/`](agentes/extraccion-evidencia/README.md), extrae effectiveness y seguridad post-autorización desde los artículos y los pasa a las planillas de extracción y de tablas de capa 1.

`.claude/agents/` y `.claude/skills/` contienen enlaces simbólicos a las definiciones que viven dentro de cada sistema, para que Claude Code las encuentre sin duplicarlas.
