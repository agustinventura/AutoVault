---
name: daily-flow-status
description: Muestra el foco actual del sistema — qué entidad está activa, su tipo, el día y (si es una tarea) su estado en la FSM. Úsalo para saber "¿en qué estoy trabajando ahora mismo?".
---

# daily-flow-status

Úsala cuando el usuario diga "¿en qué estoy?", "¿cuál es el foco?", "status", `/daily-flow-status`, o similar.

## Flujo

1. Consulta el foco actual:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-status/scripts/status.py \
     --vault-root . \
     --focus-file .focus
   ```

2. Interpreta el resultado y responde al usuario en lenguaje natural:

   - `focused: false` → "No hay foco activo en este momento."
   - `focused: true, type: task` → "Estás trabajando en [[basename]] (estado: `task_status`), desde `since`."
   - `focused: true, type: meeting` → "Estás en la reunión [[basename]], iniciada `since`."
   - Otros tipos → "El foco está en [[basename]] (`type`), desde `since`."

## Notas
- No modifica ningún archivo.
- No requiere nota diaria.
