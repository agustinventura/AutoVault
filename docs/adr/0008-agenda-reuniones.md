# ADR-0008 — Agenda parseada por el LLM; reuniones on-demand

## Contexto
Al empezar el día, el usuario da la agenda en lenguaje natural. Esa información
alimenta la sección Agenda y la lista de reuniones planificadas.

## Decisión
- El **LLM parsea** el lenguaje natural a un JSON estructurado
  (`{start, end, breaks, meetings}`), lo **confirma** con el usuario y lo pasa
  al script, que escribe (P1).
- Las notas de reunión se crean **on-demand** al empezar la reunión, no al
  empezar el día (M1). La sección Agenda de la daily es la fuente de verdad de
  las reuniones planificadas.
- El **wikilink** a la reunión se inyecta en la línea de la agenda al crearla
  (W3). La línea se localiza por el **nombre** de la reunión (L2).
- Una reunión ad-hoc inserta una línea nueva en la Agenda con la hora actual; la
  Agenda se mantiene **ordenada cronológicamente**.

## Alternativas
- **Parseo por el script** (regex): frágil ante variaciones de fraseo.
- **Materializar todas las notas de reunión al empezar el día**: crea notas de
  reuniones que pueden cancelarse y pide datos que aún no se tienen.

## Consecuencias
- Se aprovecha al LLM donde es fuerte (NL → estructura) y al script donde debe
  serlo (escritura determinista).
- Wikilinks de la agenda sin nota destino hasta que la reunión empieza: es el
  comportamiento normal de Obsidian.
