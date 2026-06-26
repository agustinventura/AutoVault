# ADR-0009 — Estado en frontmatter + tag sincronizado; walk del FS

## Contexto
`start-day` y `focus` necesitan listar tareas por estado. Las notas de tarea
están dispersas por el vault. Hay que decidir dónde vive el estado y cómo se
descubre.

## Decisión
- El estado vive en el **frontmatter** como fuente de verdad (`status: …`), y el
  tag de estado (`tarea/…`) **también** en el frontmatter, **sincronizado** por
  script (doble representación: campos para lógica/Dataview, tags para
  grafo/navegación).
- El descubrimiento se hace con un **walk del filesystem** + parseo de YAML.
- Un campo **`type`** clasifica cada nota (`task`, `ticket`, `initiative`,
  `meeting`, `project`, `org`, `daily`).

## Alternativas
- **Tag inline en el cuerpo**: cambiar de estado obliga a buscar y reemplazar en
  el texto (frágil).
- **Depender de Dataview** para descubrir: Dataview es runtime de Obsidian, no
  accesible desde un script.

## Consecuencias
- Cambiar de estado = reescribir campos YAML (trivial, determinista).
- Dataview consulta el frontmatter directamente.
- Clasificar por `type` es robusto ante movimientos de archivos.
