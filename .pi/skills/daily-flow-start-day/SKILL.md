---
name: daily-flow-start-day
description: Empieza el día de trabajo. Solicita la agenda (horario, descansos, reuniones), lista las tareas pendientes/en-curso/bloqueadas y pide hasta 3 prioridades. Crea la nota diaria con toda la información.
---

# daily-flow-start-day

Úsala cuando el usuario diga "empezar el día", "start day", "comenzar", o similar al inicio de la jornada.

## Flujo

1. Obtén la fecha actual:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. Solicita la agenda al usuario: hora de inicio, hora de fin, descansos (nombre, inicio, fin) y reuniones (nombre, inicio, fin). Acepta lenguaje natural.

3. Parsea la agenda a este JSON y **confírmala con el usuario** antes de continuar:
   ```json
   {"start":"HH:MM","end":"HH:MM","breaks":[{"name":"…","start":"HH:MM","end":"HH:MM"}],"meetings":[{"name":"…","start":"HH:MM","end":"HH:MM"}]}
   ```

4. Busca tareas activas (pendiente/en-curso/bloqueada) usando el walk del vault. Muéstralas al usuario y pídele que elija hasta 3 prioridades (basenames de las notas).

5. Crea la nota diaria:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-start-day/scripts/start_day.py \
     --vault-root . \
     --day <YYYYMMDD> \
     --agenda '<json_agenda>' \
     --priorities '<json_array_basenames>'
   ```

6. Informa al usuario del resultado (ok/error).

## Precondiciones
- Ninguna. Si la nota ya existe, el script es idempotente (no sobrescribe).

## Errores comunes
- `INVALID_JSON`: el JSON de agenda o prioridades no es válido.
- `TEMPLATE_ERROR`: la plantilla `Templates/daily_note.md` no existe.
