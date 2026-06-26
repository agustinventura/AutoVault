# ADR-0013 — Nombres de tarea asimétricos; enlaces bidireccionales

## Contexto
Las tareas se crean a partir de un ticket o de una iniciativa, con ubicaciones y
nombres distintos. Los títulos pueden contener espacios, acentos y caracteres
ilegales para el filesystem.

## Decisión
- **Asimetría intencional** de nombres:
  - Tarea de ticket: `<ID>_<Título>.md` en `<Org>/Tickets/Tasks/`.
  - Tarea de iniciativa: `<Título>.md` en `…/Iniciativas/<Iniciativa>/Tasks/`.
- El nombre de archivo se **sanea** (se reemplazan `/ \ : * ? " < > |`); el
  título real se conserva en el frontmatter (`title`) y en el cuerpo.
- Crear una tarea **valida** que el ticket/iniciativa padre exista; si no,
  **falla** con mensaje claro (no auto-crea).
- Enlace **bidireccional** tarea ↔ padre, mantenido por el script: la tarea
  enlaza a su padre y el padre lista la tarea en su sección Tareas.

## Alternativas
- **Nombres simétricos**: las tareas de ticket comparten carpeta y podrían
  colisionar por título; el prefijo del ID lo evita. Las de iniciativa ya están
  aisladas en su carpeta.
- **Auto-crear el padre**: oculta errores de flujo.

## Consecuencias
- Sin colisiones de nombre.
- Grafo navegable en ambos sentidos.
- El usuario debe crear el padre antes que la tarea.
