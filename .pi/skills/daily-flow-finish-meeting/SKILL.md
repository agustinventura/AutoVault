---
name: daily-flow-finish-meeting
description: Termina la reunión actualmente en foco. Solicita las conclusiones, las anota en la sección Conclusiones de la reunión y limpia el foco.
---

# daily-flow-finish-meeting

Úsala cuando el usuario diga "terminar la reunión", "fin de la reunión", "finish meeting", o similar.

## Flujo

1. Solicita las conclusiones de la reunión.

2. Termina la reunión:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-finish-meeting/scripts/finish_meeting.py \
     --vault-root . \
     --focus-file .focus \
     --conclusion '<conclusiones>'
   ```

3. Confirma al usuario que la reunión ha terminado y que el foco ha quedado vacío.
   Recuerda al usuario que puede usar `/daily-flow-focus` para retomar una tarea.

## Precondiciones
- `.focus` debe apuntar a una reunión (`NO_MEETING_FOCUS` → sugiere `/daily-flow-start-meeting`).
