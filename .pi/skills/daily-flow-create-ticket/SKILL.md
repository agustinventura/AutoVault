---
name: daily-flow-create-ticket
description: Crea un nuevo ticket en el vault. Solicita la organización, el proyecto, el ID del ticket, título, objetivo y descripción tal como aparece en el sistema de ticketing.
---

# daily-flow-create-ticket

Úsala cuando el usuario diga "crear ticket", "nuevo ticket", o similar.

## Flujo

1. Solicita: organización, proyecto, ID del ticket (p.ej. ONLINE-173894), título, objetivo (target) y descripción original del ticket.

2. Crea el ticket:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-create-ticket/scripts/create_ticket.py \
     --vault-root . \
     --org '<org>' \
     --project '<proyecto>' \
     --id '<ID>' \
     --title '<título>' \
     --target '<objetivo>' \
     --description '<descripción>'
   ```

3. Informa del resultado. El ticket queda enlazado en la sección "Enlaces" del proyecto.

## Errores comunes
- `PROJECT_NOT_FOUND`: el proyecto no existe → sugiere `/daily-flow-create-project`.
