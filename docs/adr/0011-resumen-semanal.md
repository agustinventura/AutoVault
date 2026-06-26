# ADR-0011 — Resumen semanal: script recopila, LLM redacta

## Contexto
Los viernes se genera un resumen semanal. Redactar prosa es tarea del LLM;
recopilar datos es determinista.

## Decisión
- Un script **recopila** datos crudos de la semana en JSON: tareas terminadas en
  la semana, tickets e iniciativas tocados, notas de las dailies.
- El **LLM redacta** las secciones de prosa (tareas completadas, resumen de
  tickets, resumen de iniciativas).
- Un script **escribe** el `W-NN.md` a partir de la plantilla.
- Rango: numeración de semana **ISO** (`W-NN`), recopilando de **lunes a
  viernes**.
- Las **prioridades de la semana siguiente** son input del usuario, tras
  presentar lo anterior.
- `end-day` **detecta** que es viernes (vía `now`) y ofrece generar el resumen.

## Alternativas
- **Que el LLM también recopile**: no determinista para los datos.

## Consecuencias
- Para saber qué tareas se terminaron en la semana se añade el campo `done`
  (fecha) al frontmatter de la tarea al terminarla (ver esquema en la spec
  técnica).
