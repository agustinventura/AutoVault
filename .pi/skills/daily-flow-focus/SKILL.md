---
name: daily-flow-focus
description: Focaliza una entidad del vault (tarea, ticket, iniciativa, proyecto u organización). Todo lo que se escriba a continuación se vuelca en la sección Notas de esa entidad. Si es una tarea, la marca como en-curso.
---

# daily-flow-focus

Úsala cuando el usuario diga "focalizar", "focus en", "quiero trabajar en", o similar.

## Flujo

1. Obtén la fecha y hora actuales:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. Obtén el foco actual:
   ```
   .pi/skills/.venv/bin/python -m vault.focus get --focus-file .focus
   ```

3. Pregunta qué entidad quiere focalizar. Si el usuario no lo especifica, muéstrale las tareas pendientes/bloqueadas/en-curso y que elija.

4. Establece el foco:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-focus/scripts/focus.py \
     --vault-root . \
     --path '<ruta_relativa>' \
     --type '<task|ticket|initiative|project|org|meeting>' \
     --day <YYYYMMDD> \
     --time <HH:MM> \
     --focus-file .focus
   ```

5. Confirma al usuario qué entidad está en foco.

## Precondiciones
- Debe existir la nota diaria del día (`NO_DAILY` → sugiere `/daily-flow-start-day`).
- La nota de la entidad debe existir (`NOTE_NOT_FOUND` → sugiere la skill de creación).

## Comportamiento post-focus
A partir de este momento, todo texto libre que escriba el usuario se appendea a la sección Notas de la entidad en foco mediante:
```
.pi/skills/.venv/bin/python -m vault.notes append \
  --file '<ruta>' --day <YYYYMMDD> --text '- HH:MM <texto>'
```
