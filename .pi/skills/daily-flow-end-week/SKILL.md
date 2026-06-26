---
name: daily-flow-end-week
description: Genera el resumen semanal. Recopila tareas completadas, tickets e iniciativas trabajados durante la semana, presenta la información al usuario, le pide las prioridades para la semana siguiente y escribe la nota W-NN.md.
---

# daily-flow-end-week

Úsala cuando el usuario diga "resumen semanal", "end week", o cuando `end-day` detecte que es viernes y el usuario confirme.

## Flujo

1. Obtén la fecha actual y el rango lunes-viernes:
   ```
   .pi/skills/.venv/bin/python -m vault.now
   ```

2. **Recopila** (tú, el agente) leyendo el vault:
   - Tareas con `status: terminada` y `done` dentro del rango lunes-viernes.
   - Tickets e iniciativas que tengan bullets `[[YYYYMMDD]]` de días de esa semana en sus secciones Notas.
   - Notas de las dailies de la semana.

3. **Redacta** los resúmenes de tickets e iniciativas basándote en los datos recopilados.

4. Presenta la información al usuario y solicita las **prioridades para la semana siguiente**.

5. Escribe el resumen semanal:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-end-week/scripts/end_week.py \
     --vault-root . \
     --day <YYYYMMDD> \
     --week-label <W-NN> \
     --iso-week <AAAA-Www> \
     --date-from <AAAA-MM-DD> \
     --date-to <AAAA-MM-DD> \
     --completed-tasks '<json_lista>' \
     --tickets-summary '<texto>' \
     --initiatives-summary '<texto>' \
     --priorities '<json_lista>'
   ```

## Nota
El script solo escribe; la recopilación y redacción es responsabilidad del agente.
