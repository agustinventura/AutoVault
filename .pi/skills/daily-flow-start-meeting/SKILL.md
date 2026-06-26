---
name: daily-flow-start-meeting
description: Empieza una reunión. Puede ser una reunión planificada de la agenda del día o una ad-hoc. Solicita la organización, proyecto, nombre, participantes y objetivo. Si había una tarea en foco, la pasa a pendiente.
---

# daily-flow-start-meeting

Úsala cuando el usuario diga "empezar reunión", "tengo una reunión", "start meeting", o similar.

## Flujo

1. Obtén la fecha y hora actuales:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. Pregunta si la reunión estaba en la agenda del día o es nueva (ad-hoc).

3. Solicita los datos necesarios:
   - Organización y proyecto.
   - Nombre exacto de la reunión (para que coincida con la agenda si no es ad-hoc).
   - Participantes (separados por comas).
   - Objetivo de la reunión.

4. Inicia la reunión:

   Si estaba en la agenda:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-start-meeting/scripts/start_meeting.py \
     --vault-root . \
     --day <YYYYMMDD> --time <HH:MM> \
     --org '<org>' --project '<proyecto>' \
     --name '<nombre>' \
     --participants '<lista>' \
     --goal '<objetivo>' \
     --focus-file .focus
   ```

   Si es ad-hoc (añadir `--ad-hoc`):
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-start-meeting/scripts/start_meeting.py \
     --vault-root . \
     --day <YYYYMMDD> --time <HH:MM> \
     --org '<org>' --project '<proyecto>' \
     --name '<nombre>' \
     --participants '<lista>' \
     --goal '<objetivo>' \
     --focus-file .focus \
     --ad-hoc
   ```

5. Confirma al usuario qué reunión está en foco. A partir de ahora, todo texto libre se vuelca en "Notas" de la reunión.

## Notas
- Si había una tarea en foco, se pasa automáticamente a `pendiente`.
- Si había otra reunión en foco, se cierra automáticamente (sin conclusiones).
