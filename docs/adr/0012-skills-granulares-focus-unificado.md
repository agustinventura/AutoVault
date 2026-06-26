# ADR-0012 — Una skill por acción; foco unificado

## Contexto
La especificación describe ~14 acciones. Pi elige la skill por su `name` y
`description`. Hay que decidir la granularidad de las skills.

## Decisión
- **Una skill por acción** (~14 skills), prefijo `daily-flow-`.
- **Foco unificado**: una sola skill `focus` acepta cualquier entidad (tarea,
  ticket, iniciativa, proyecto, organización). Solo focalizar una **tarea**
  produce transición de estado (→ en-curso); para el resto, `focus` solo cambia
  el destino de las notas.
- Crear organización y proyecto también son skills con su propio script.

## Alternativas
- **Skills agrupadas por entidad** con subcomando: añade parseo de sub-acción y
  descripciones menos precisas para el discovery.
- **Focus separado por tipo de entidad**: más comandos para el mismo gesto
  mental.

## Consecuencias
- Descripciones de skill precisas → invocación correcta por el agente.
- "Focalizar aquí" es un único comando.
- Más carpetas de skill, cada una mínima.
