# ADR-0018 — Foco/notas exigen daily; crear entidades no

## Contexto
Focalizar y tomar notas necesitan la nota diaria (para el ancla `[[YYYYMMDD]]` y
la sección "Trabajado hoy"). Crear estructura (organizaciones, proyectos,
tickets, iniciativas, tareas) es trabajo independiente del día.

## Decisión
- `focus` y la captura de notas **exigen** que exista la nota diaria del día; si
  no, **fallan** pidiendo empezar el día primero.
- **Crear** entidades es **independiente** del día: funciona sin nota diaria y
  no toca "Trabajado hoy" ni notas con `[[día]]`.
- Se asume la **hora local** del sistema (asistente personal mono-usuario, sin
  manejo de zonas horarias).

## Alternativas
- **Auto-crear una daily mínima** al focalizar sin día: oculta el flujo de
  empezar el día.

## Consecuencias
- El día siempre arranca explícitamente con `start-day`.
- La estructura del vault puede prepararse en cualquier momento.
