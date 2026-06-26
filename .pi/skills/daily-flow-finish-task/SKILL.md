---
name: daily-flow-finish-task
description: Termina la tarea actualmente en foco. Solicita las conclusiones, las anota en la sección Notas y marca la tarea como terminada. Limpia el foco.
---

# daily-flow-finish-task

Úsala cuando el usuario diga "terminar la tarea", "tarea completada", "finish task", o similar.

## Flujo

1. Obtén la fecha y hora actuales:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. Solicita las conclusiones de la tarea.

3. Termina la tarea:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-finish-task/scripts/finish_task.py \
     --vault-root . \
     --focus-file .focus \
     --conclusion '<conclusiones>' \
     --day <YYYYMMDD> \
     --time <HH:MM>
   ```

4. Confirma al usuario que la tarea está terminada y que el foco ha quedado vacío.
   Recuerda al usuario que puede continuar con `/daily-flow-focus` para elegir la siguiente tarea.

## Precondiciones
- `.focus` debe apuntar a una tarea (`NO_TASK_FOCUS` → sugiere `/daily-flow-focus`).
