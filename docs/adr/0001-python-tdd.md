# ADR-0001 — Python + TDD estricto

## Contexto
Las acciones deterministas del sistema (copiar plantillas, reescribir Markdown,
gestionar estados) se implementan con scripts. La especificación obliga a elegir
un único lenguaje.

## Decisión
**Python**, con desarrollo guiado por **TDD estricto** (red-green-refactor).

## Alternativas
- **Bash**: sufre con rutas con espacios (frecuentes en el vault: "Charla
  Multiagentes", "Adaptar Presentación") y con el parseo de Markdown/YAML.

## Consecuencias
- Manipulación robusta de Markdown, frontmatter (YAML) y fechas (semana ISO).
- Multiplataforma.
- Todo script se escribe con un test que falla primero; sin umbral numérico de
  cobertura (métrica informativa).
