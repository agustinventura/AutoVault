# ADR-0007 — Captura de notas: append inmediato por script

## Contexto
El agente es conversacional. Hay que decidir qué cuenta como "nota a volcar" y
cómo se persiste de forma fiable.

## Decisión
Append **inmediato** vía script por cada turno que sea una nota. El formato:

- Cada nota es un bullet con timestamp: `- HH:MM texto`.
- Bajo un ancla por día `[[YYYYMMDD]]` dentro de la sección Notas.
- El script es **idempotente** respecto al ancla: si `[[YYYYMMDD]]` no existe lo
  inserta; si existe, solo añade el bullet.

## Alternativas
- **Comando explícito de volcado**: más fricción.
- **Buffer en memoria con flush diferido**: riesgo de pérdida si la sesión muere.

## Consecuencias
- Persistencia inmediata (sin pérdida ante caídas).
- La escritura (localizar sección, formatear) es determinista en el script; el
  agente solo aporta el texto y el día.
- El agente decide turno a turno si un mensaje es nota o comando (ver ADR-0012 y
  AGENTS.md).
