---
name: daily-flow-create-task
description: Crea una nueva tarea en el vault, asociada a un ticket o a una iniciativa. Solicita el origen (ticket o iniciativa), el título y la descripción.
---

# daily-flow-create-task

Úsala cuando el usuario diga "crear tarea", "nueva tarea", o similar.

## Flujo

1. Pregunta si la tarea viene de un **ticket** o de una **iniciativa**.

2a. Si viene de ticket, solicita: organización, ID del ticket, título, descripción.
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-create-task/scripts/create_task.py \
     --vault-root . \
     --org '<org>' \
     --ticket '<ID>' \
     --title '<título>' \
     --description '<descripción>'
   ```

2b. Si viene de iniciativa, solicita: organización, proyecto, nombre de la iniciativa, título, descripción.
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-create-task/scripts/create_task.py \
     --vault-root . \
     --org '<org>' \
     --project '<proyecto>' \
     --initiative '<nombre>' \
     --title '<título>' \
     --description '<descripción>'
   ```

3. Informa del resultado. La tarea queda en estado `pendiente` y enlazada en "Tareas" del padre.

## Errores comunes
- `PARENT_NOT_FOUND`: el ticket o iniciativa no existe → sugiere la skill de creación.
