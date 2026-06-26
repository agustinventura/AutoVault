# ADR-0005 — `.focus` como JSON; sin memoria de tarea previa

## Contexto
El sistema necesita saber en qué entidad está el foco para enrutar las notas y
validar comandos. Algunas transiciones dependen del **tipo** de lo focalizado
(solo las tareas cambian de estado).

## Decisión
`.focus` es un **JSON** con `{path, type, day, since}`. Ausencia del archivo o
contenido vacío significa **sin foco**.

Tras terminar una reunión el foco queda **vacío**: no se restaura ni se recuerda
la tarea que estaba en foco antes de la reunión.

## Alternativas
- **Ruta en texto plano**: obligaría a inferir el tipo desde la ruta (frágil).
- **Guardar la tarea previa** para sugerir retomarla tras la reunión: añade
  estado efímero; se descartó por simplicidad (la tarea queda como pendiente y
  se vuelve a elegir explícitamente).

## Consecuencias
- `type` explícito → transiciones deterministas sin parsear rutas.
- `day` permite construir el ancla `[[YYYYMMDD]]` sin recalcular la fecha.
- Tras una reunión hay que volver a `focus` para continuar.
