# ADR-0010 — Plantillas con placeholders mustache

## Contexto
Las skills crean notas a partir de plantillas. Hay que decidir el mecanismo de
relleno.

## Decisión
Plantillas `.md` en `Templates/` con placeholders **`{{token}}`** (estilo
mustache). El script lee la plantilla, sustituye los tokens y escribe. Las
secciones aparecen con su encabezado y el **cuerpo vacío**.

## Alternativas
- **Generación 100% en Python**: la "plantilla" dejaría de ser un `.md`
  editable.
- **Sintaxis `${token}` o `{token}`**: `{token}` colisiona con `{` de Dataview
  inline; `{{ }}` es la convención reconocida en Obsidian y no choca con Markdown.

## Consecuencias
- Las plantillas son editables sin tocar código.
- Relleno determinista y testeable (plantilla + datos → salida esperada).
- Las plantillas reales se usan como entrada en los tests de integración.
- Los headers vacíos son el punto de anclaje para el append de notas.
