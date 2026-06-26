# ADR-0016 — Errores: exit code + JSON; sin log; script faltante solo avisa

## Contexto
Los scripts pueden fallar (padre inexistente, transición ilegal, precondición no
cumplida). El agente debe reaccionar de forma predecible.

## Decisión
- Contrato de salida: **exit code + JSON** en stdout.
  - Éxito: exit 0 + `{"ok": true, …}`.
  - Fallo: exit ≠ 0 + `{"ok": false, "error": "<mensaje legible>", "code": "<CODE>"}`.
- Ante `ok: false`, el agente **muestra el error**, sugiere la skill de remedio
  cuando aplique y **no** ejecuta acciones manuales.
- **Sin log** separado: el propio vault (notas con timestamp) es la auditoría.
- Si una acción requerida **no tiene script/skill**, el agente lo **avisa**
  explícitamente y **no** ofrece implementarlo sobre la marcha.

## Alternativas
- **Solo exit code**: pierde el mensaje legible.
- **Fichero de log de acciones**: redundante con el vault.

## Consecuencias
- El agente reacciona de forma determinista a los fallos.
- Se respeta la regla de oro: nunca hacer a mano lo que corresponde a un script.
