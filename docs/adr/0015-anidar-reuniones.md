# ADR-0015 — Las reuniones se anidan (cierre automático de la previa)

## Contexto
Puede empezarse una reunión teniendo otra en foco. Es poco frecuente y, cuando
ocurre, suele ser urgente.

## Decisión
Las reuniones **se anidan**: empezar una reunión con otra en foco **cierra
automáticamente** la anterior, sin pedir conclusiones, dejando una marca de
cierre automático en sus Conclusiones (por ejemplo, *"Reunión cerrada
automáticamente al iniciar [[…]]"*).

En este encadenamiento no hay efecto adicional sobre tareas: si había una tarea,
ya pasó a pendiente al empezar la primera reunión (sin memoria de tarea, ADR-0005).

## Alternativas
- **Exigir cerrar la reunión previa** (con conclusiones) antes de empezar otra:
  introduce fricción justo en el momento urgente que se quería evitar.

## Consecuencias
- Cero fricción al encadenar reuniones.
- La reunión previa puede completarse a mano más tarde si se desea.
