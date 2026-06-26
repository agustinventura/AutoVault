# ADR-0017 — Sección "Trabajado hoy" en la nota diaria

## Contexto
Conviene reflejar en la nota diaria qué entidades se han tocado durante el día.

## Decisión
La nota diaria tiene una sección **"Trabajado hoy"** que lista, como wikilinks,
las entidades focalizadas durante el día, con la **hora del primer foco**
(`- HH:MM [[entidad]]`).

- La mantienen `focus` y `start-meeting`.
- **Entrada única por entidad**: refocalizar la misma entidad no la duplica.

## Alternativas
- **No tener la sección** y reconstruir "qué se tocó el día X" desde el lado de
  cada entidad (vía el ancla `[[YYYYMMDD]]`): válido, pero se prefiere la vista
  directa en la daily.

## Consecuencias
- Timeline de qué se tocó y cuándo, en la propia nota diaria.
- Los scripts de foco y de inicio de reunión actualizan esta sección de forma
  idempotente.
