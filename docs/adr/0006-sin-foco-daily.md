# ADR-0006 — Sin foco, las notas van a la nota diaria

## Contexto
El foco puede quedar vacío (recién empezado el día, tras terminar una tarea o
una reunión). Hay que decidir dónde va el texto libre que el usuario escriba en
ese estado.

## Decisión
Sin foco activo, las notas se vuelcan en la sección **Notes** de la nota diaria,
con un **aviso único** ("sin foco activo, anotando en la daily…").

## Alternativas
- **Bloquear y exigir foco**: fricción alta en cada hueco entre tareas.
- **Preguntar cada vez**: demasiada fricción conversacional.

## Consecuencias
- Nunca se pierde texto: siempre hay destino.
- La sección Notes de la daily cumple su función de apuntes no estructurados del
  día.
- Requiere que exista la nota diaria (ver ADR-0018).
