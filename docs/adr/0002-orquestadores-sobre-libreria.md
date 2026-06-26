# ADR-0002 — Orquestadores sobre librería compartida

## Contexto
Cada skill invoca scripts para sus acciones deterministas. Hay que decidir la
granularidad de esos scripts.

## Decisión
Un **orquestador por skill** (un script por acción) que compone una **librería
compartida** `vault` de primitivas.

## Alternativas
- **Primitivas atómicas** que el agente compone: el agente encadenaría varias
  llamadas, con más superficie de error y menos determinismo.
- **Scripts monolíticos sin librería**: duplicación de lógica.

## Consecuencias
- Más determinista: el agente invoca un comando por acción.
- TDD favorecido: la librería se testea en unitarios rápidos; los orquestadores
  en integración.
- La lógica compartida (rutas, Markdown, FSM) no se duplica.
