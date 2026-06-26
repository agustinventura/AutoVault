---
name: daily-flow-create-org
description: Crea una nueva organización en el vault (carpeta + nota). Solicita el nombre de la organización.
---

# daily-flow-create-org

Úsala cuando el usuario diga "crear organización", "nueva organización", o similar.

## Flujo

1. Solicita el nombre de la organización.

2. Crea la organización:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-create-org/scripts/create_org.py \
     --vault-root . \
     --name '<nombre>'
   ```

3. Informa del resultado.

## Precondiciones
- Ninguna. Idempotente.
