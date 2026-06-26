---
name: daily-flow-end-day
description: Cierra el día de trabajo. Solicita una reflexión y las tareas pendientes para mañana, las escribe en la sección Day close out de la nota diaria. Si es viernes, ofrece generar el resumen semanal.
---

# daily-flow-end-day

Úsala cuando el usuario diga "cerrar el día", "fin del día", "end day", o similar al terminar la jornada.

## Flujo

1. Obtén la fecha actual:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. Solicita al usuario:
   - Una reflexión libre del día.
   - Lista de tareas pendientes para mañana (basenames, pueden ser wikilinks).

3. Cierra el día:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-end-day/scripts/end_day.py \
     --vault-root . \
     --day <YYYYMMDD> \
     --reflection '<texto>' \
     --pending '<json_array_basenames>'
   ```

4. Si el campo `is_friday` del resultado es `true`, pregunta al usuario si quiere generar el resumen semanal y lanza `/daily-flow-end-week` si confirma.

## Precondiciones
- Debe existir la nota diaria del día (`NO_DAILY`).
