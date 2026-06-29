---
name: daily-flow-start-meeting
description: Empieza una reunión. Puede ser planificada o ad-hoc. Pregunta si necesita nota propia o si las notas van directamente en la daily (inline). Si había una tarea en foco, la pasa a pendiente.
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
   - Nombre de la reunión.
   - Participantes (separados por comas).
   - Objetivo.

4. **Pregunta si la reunión necesita nota propia o si es inline** (las notas van directamente en la sección Notes de la daily bajo un subencabezado `### Nombre`). Orienta al usuario: dailies, weeklies y reuniones recurrentes cortas suelen ser buenas candidatas a inline.

5a. **Con nota propia** (sin `--inline`):
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-start-meeting/scripts/start_meeting.py \
     --vault-root . \
     --day <YYYYMMDD> --time <HH:MM> \
     --org '<org>' --project '<proyecto>' \
     --name '<nombre>' \
     --participants '<lista>' \
     --goal '<objetivo>' \
     --focus-file .focus [--ad-hoc]
   ```
   Las notas van a la sección **Notas** de la nota propia de la reunión. La reunión se añade a **Enlaces** del proyecto.

5b. **Inline** (con `--inline`):
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-start-meeting/scripts/start_meeting.py \
     --vault-root . \
     --day <YYYYMMDD> --time <HH:MM> \
     --org '<org>' --project '<proyecto>' \
     --name '<nombre>' \
     --participants '<lista>' \
     --goal '<objetivo>' \
     --focus-file .focus [--ad-hoc] \
     --inline
   ```
   Las notas van al subencabezado `### Nombre` dentro de **Notes** de la nota diaria. No se crea nota de reunión; no se añade enlace al proyecto.

6. Confirma qué reunión está en foco.

## Notas
- Si había una tarea en foco, pasa automáticamente a `pendiente`.
- Si había otra reunión en foco, se cierra automáticamente (sin conclusiones).
- Para reuniones inline, `finish-meeting` añade la conclusión en el mismo subencabezado de la daily.
