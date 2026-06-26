# ADR-0014 — Las tareas no se listan en Enlaces del proyecto

## Contexto
La especificación menciona que la sección Enlaces del proyecto incluye "tareas".
Pero las tareas ya aparecen en la sección Tareas de su ticket/iniciativa.

## Decisión
Las tareas **no** se listan en Enlaces del proyecto. Cuelgan de su
ticket/iniciativa, que sí está en Enlaces del proyecto. La navegación es
jerárquica: proyecto → ticket/iniciativa → tarea.

Los scripts mantienen automáticamente Enlaces del proyecto cuando se crea un
ticket, una iniciativa o una reunión (lo cual **exige** que el proyecto exista).

## Alternativas
- **Listar también las tareas en Enlaces del proyecto**: duplica información y
  añade ruido. (Se considera un error de la especificación original.)

## Consecuencias
- Enlaces del proyecto queda limpio (reuniones, tickets, iniciativas).
- El grafo se recorre por niveles.
