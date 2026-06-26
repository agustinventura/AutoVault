---
name: daily-flow-create-project
description: Crea un nuevo proyecto en el vault. Solicita la organización, el nombre del proyecto y su descripción.
---

# daily-flow-create-project

Úsala cuando el usuario diga "crear proyecto", "nuevo proyecto", o similar.

## Flujo

1. Solicita: organización, nombre del proyecto, descripción.

2. Crea el proyecto:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-create-project/scripts/create_project.py \
     --vault-root . \
     --org '<org>' \
     --name '<nombre>' \
     --description '<descripción>'
   ```

3. Informa del resultado.

## Errores comunes
- `ORG_NOT_FOUND`: la organización no existe → sugiere `/daily-flow-create-org`.
