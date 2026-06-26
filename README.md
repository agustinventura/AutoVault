# auto_vault — Asistente de productividad diaria

Sistema de productividad personal para ingeniería de software. Un asistente de
IA actúa como secretario personal: captura por consola, de forma rápida y
estructurada, las notas de reuniones y trabajo técnico diario. La lectura se
hace con **Obsidian** (wikilinks, tags, Dataview). Toda la información se guarda
como Markdown en este vault.

## Qué es

- **Entrada**: agente conversacional (Pi) ejecutado desde la raíz del vault.
- **Lectura**: Obsidian.
- **Acciones deterministas**: scripts Python orquestados por *skills*
  `daily-flow-*`. El agente nunca hace a mano lo que un script puede hacer.

El día se gestiona como una máquina de estados: se empieza el día (agenda +
prioridades), se **focaliza** trabajo (las notas se vuelcan a la entidad en
foco), se gestionan reuniones y tareas, y se cierra el día. Los viernes se
genera un resumen semanal.

## Inicialización

Requiere [`uv`](https://docs.astral.sh/uv/). Una sola vez:

```bash
./bootstrap.sh
```

Crea el entorno virtual en `.pi/skills/.venv` e instala la librería `vault`.

Verificar:

```bash
.pi/skills/.venv/bin/python -m pytest .pi/skills/
```

## Uso

Ejecutar el agente desde la raíz del vault (`auto_vault/`) y usar los comandos:

| Comando | Para |
|---|---|
| `/daily-flow-start-day` | Empezar el día (agenda + prioridades) |
| `/daily-flow-focus` | Focalizar una tarea/ticket/iniciativa/proyecto/organización |
| `/daily-flow-create-task` | Crear una tarea |
| `/daily-flow-create-ticket` | Crear un ticket |
| `/daily-flow-create-initiative` | Crear una iniciativa |
| `/daily-flow-create-project` | Crear un proyecto |
| `/daily-flow-create-org` | Crear una organización |
| `/daily-flow-block-task` | Bloquear la tarea en foco |
| `/daily-flow-finish-task` | Terminar la tarea en foco |
| `/daily-flow-start-meeting` | Empezar una reunión |
| `/daily-flow-finish-meeting` | Terminar la reunión en foco |
| `/daily-flow-end-day` | Cerrar el día (reflexión + tareas para mañana) |
| `/daily-flow-end-week` | Generar el resumen semanal |

Escribir texto que no es un comando se interpreta como **nota** y se vuelca en
la entidad en foco (o en la nota diaria si no hay foco).

## Documentación

- [`docs/especificacion-usuario.md`](docs/especificacion-usuario.md) — metodología y flujo de trabajo.
- [`docs/especificacion-tecnica.md`](docs/especificacion-tecnica.md) — implementación.
- [`docs/adr/`](docs/adr/) — decisiones de diseño.
