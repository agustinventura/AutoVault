---
name: daily-flow-create-initiative
description: Crea una nueva iniciativa (trabajo no formalizado en un sistema externo) en el vault. Solicita la organización, el proyecto, el nombre y la descripción.
---

# daily-flow-create-initiative

Úsala cuando el usuario diga "crear iniciativa", "nueva iniciativa", o similar.

## Flujo

1. Solicita: organización, proyecto, nombre de la iniciativa, descripción.

2. Crea la iniciativa:
   ```
   .pi/skills/.venv/bin/python .pi/skills/daily-flow-create-initiative/scripts/create_initiative.py \
     --vault-root . \
     --org '<org>' \
     --project '<proyecto>' \
     --name '<nombre>' \
     --description '<descripción>'
   ```

3. Informa del resultado. La iniciativa queda enlazada en "Enlaces" del proyecto.

## Errores comunes
- `PROJECT_NOT_FOUND`: el proyecto no existe → sugiere `/daily-flow-create-project`.
