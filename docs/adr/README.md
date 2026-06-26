# Architecture Decision Records

Registro de las decisiones de diseño del asistente, con su contexto,
alternativas consideradas y consecuencias. Formato breve.

| # | Decisión |
|---|---|
| [0001](0001-python-tdd.md) | Python + TDD estricto |
| [0002](0002-orquestadores-sobre-libreria.md) | Orquestadores sobre librería compartida |
| [0003](0003-ubicacion-skills-y-codigo.md) | Skills y código en `.pi/skills/`, librería editable |
| [0004](0004-uv-venv-invocacion.md) | uv, venv único e invocación con intérprete absoluto |
| [0005](0005-focus-json.md) | `.focus` como JSON; sin memoria de tarea previa |
| [0006](0006-sin-foco-daily.md) | Sin foco, las notas van a la nota diaria |
| [0007](0007-captura-notas.md) | Captura de notas: append inmediato por script |
| [0008](0008-agenda-reuniones.md) | Agenda parseada por el LLM; reuniones on-demand |
| [0009](0009-estado-en-frontmatter.md) | Estado en frontmatter + tag sincronizado; walk del FS |
| [0010](0010-plantillas-placeholders.md) | Plantillas con placeholders mustache |
| [0011](0011-resumen-semanal.md) | Resumen semanal: script recopila, LLM redacta |
| [0012](0012-skills-granulares-focus-unificado.md) | Una skill por acción; foco unificado |
| [0013](0013-nombres-y-enlaces-tareas.md) | Nombres de tarea asimétricos; enlaces bidireccionales |
| [0014](0014-tareas-fuera-de-enlaces-proyecto.md) | Las tareas no se listan en Enlaces del proyecto |
| [0015](0015-anidar-reuniones.md) | Las reuniones se anidan (cierre automático de la previa) |
| [0016](0016-protocolo-errores.md) | Errores: exit code + JSON; sin log; script faltante solo avisa |
| [0017](0017-trabajado-hoy.md) | Sección "Trabajado hoy" en la nota diaria |
| [0018](0018-dia-activo-requerido.md) | Foco/notas exigen daily; crear entidades no |
