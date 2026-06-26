# ADR-0003 — Skills y código en `.pi/skills/`, librería editable

## Contexto
Pi descubre skills en `<cwd>/.pi/skills/`. Hay que decidir dónde vive el código
Python y cómo se relaciona con las skills, sin contaminar ni el discovery de Pi
ni el grafo de Obsidian.

## Decisión
- Skills en `auto_vault/.pi/skills/<accion>/SKILL.md`, versionadas con el repo.
- El código de cada skill vive **dentro de su propia carpeta** (`scripts/`,
  `tests/`).
- La librería compartida es un paquete en `.pi/skills/_lib/`, instalado en modo
  **editable**; los scripts hacen `import vault.*`.

## Alternativas
- **Paquete único** con las acciones como módulos (`vault.actions.*`) y las
  carpetas de skill solo con `SKILL.md`: rechazado por preferir skills
  autocontenidas.
- **Código fuera del vault**: separa el repo en dos ubicaciones.

## Consecuencias
- Pi no recursa dentro de una carpeta con `SKILL.md`, así que el código junto a
  cada skill no afecta al discovery.
- `.pi/` es un dotdir: Obsidian lo ignora.
- `_lib/` no tiene `SKILL.md` ni `.md` sueltos en su raíz → no se registra como
  skill.
- Requiere instalar `_lib` editable (ver ADR-0004).
