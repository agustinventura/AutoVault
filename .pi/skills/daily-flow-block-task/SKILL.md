---
name: daily-flow-block-task
description: Bloquea la tarea actualmente en foco. Solicita el motivo del bloqueo, lo anota en la sección Notas de la tarea y cambia su estado a bloqueada.
---

# daily-flow-block-task

Úsala cuando el usuario diga "bloquear la tarea", "está bloqueada", "block task", o similar.

## Flujo

1. Obtén la fecha y hora actuales:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. Solicita el motivo del bloqueo.

3. Bloquea la tarea:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-block-task/scripts/block_task.py \
     --vault-root . \
     --focus-file .focus \
     --reason '<motivo>' \
     --day <YYYYMMDD> \
     --time <HH:MM>
   ```

4. Confirma al usuario que la tarea está bloqueada.

## Precondiciones
- `.focus` debe apuntar a una tarea (`NO_TASK_FOCUS` → sugiere `/daily-flow-focus`).
