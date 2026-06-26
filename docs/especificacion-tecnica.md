# Especificación técnica — Asistente de productividad diaria

> Cómo se implementa el sistema descrito en
> [`especificacion-usuario.md`](especificacion-usuario.md). Las decisiones de
> diseño con sus alternativas y razones están en [`adr/`](adr/).

## 1. Arquitectura

- **Entrada**: agente conversacional ligero (Pi /
  `@earendil-works/pi-coding-agent`) ejecutado con `cwd` = raíz del vault.
- **Lectura**: Obsidian (wikilinks, tags, Dataview).
- **Acciones deterministas**: scripts Python. El agente **nunca** realiza
  manualmente una acción que pueda hacer un script. Si falta un script para una
  acción requerida, el agente lo **avisa** y espera (no improvisa, no ofrece
  implementarlo sobre la marcha).
- **Patrón**: orquestadores (un script por skill) sobre una **librería
  compartida** `vault`. La lógica determinista vive en la librería; los
  orquestadores la componen. Ver [ADR-0002](adr/0002-orquestadores-sobre-libreria.md).

### 1.1. Estructura del repositorio

```
auto_vault/                       cwd de Pi + vault Obsidian (hora local del sistema)
├── README.md                     punto de entrada rápido
├── bootstrap.sh                  crea venv + instala `vault` editable (ejecución única)
├── .gitignore
├── .focus                        estado de la FSM (JSON; ausente/vacío = sin foco)
├── .obsidian/
├── docs/                         documentación (visible en Obsidian)
│   ├── especificacion-usuario.md
│   ├── especificacion-tecnica.md
│   └── adr/                      Architecture Decision Records
├── Templates/                    8 plantillas .md con placeholders {{mustache}}
├── Daily log/ , <Org>/ …         datos del vault (se crean en uso)
└── .pi/skills/                   Pi descubre skills aquí (dotdir → Obsidian lo ignora)
    ├── .venv/                    entorno único (git-ignored, recreable)
    ├── _lib/                     paquete `vault` (NO es skill: sin SKILL.md)
    │   ├── pyproject.toml
    │   ├── src/vault/            módulos de la librería
    │   └── tests/               tests unitarios (lógica pura)
    └── daily-flow-<accion>/      una carpeta por skill
        ├── SKILL.md              name + description (discovery) + invocación
        ├── scripts/<x>.py        orquestador (import vault.*)
        └── tests/test_<x>.py     tests de integración (tmp_path)
```

### 1.2. Descubrimiento de skills por Pi

Pi escanea solo dos ubicaciones: `~/.pi/agent/skills/` (global) y
`<cwd>/.pi/skills/` (proyecto). Una carpeta con `SKILL.md` es una skill y **no**
se recursa dentro de ella; los `.md` y el código que contiene son invisibles al
discovery. Por eso el código Python puede convivir dentro de cada carpeta de
skill sin contaminar el descubrimiento. `_lib/` no tiene `SKILL.md` ni `.md`
sueltos en su raíz, por lo que tampoco se registra como skill.

## 2. Entorno y ejecución

- Gestor de entorno: **uv**. Ver [ADR-0004](adr/0004-uv-venv-invocacion.md).
- Entorno virtual **único** en `.pi/skills/.venv`, con la librería `vault`
  instalada en modo editable (`uv pip install -e _lib[dev]`).
- **Invocación de orquestadores** (relativa a `cwd`, sin activar el venv):

  ```
  .pi/skills/.venv/bin/python .pi/skills/daily-flow-<accion>/scripts/<x>.py --args
  ```

- **Utilidades compartidas** (sin skill propia), como módulos ejecutables del
  paquete:

  ```
  .pi/skills/.venv/bin/python -m vault.now
  .pi/skills/.venv/bin/python -m vault.focus get
  .pi/skills/.venv/bin/python -m vault.notes append --text "…"
  ```

## 3. Librería `vault`

| Módulo | Responsabilidad |
|---|---|
| `dates` | `YYYYMMDD`, `HH:MM`, día de la semana, número de semana ISO, detección de viernes (lógica pura). |
| `now` | Ejecutable: emite fecha/hora/semana/viernes como JSON. Capa fina de I/O sobre `dates`. |
| `paths` | Construcción y validación de rutas del vault; saneo de nombres de archivo. |
| `markdown` | Parseo/localización/reescritura de secciones por encabezado; lectura/escritura de frontmatter YAML. |
| `tasks` | Tabla de transiciones de la FSM y su validación; walk del filesystem por estado; sincronización `status` ↔ tag. |
| `templates` | Copia de plantilla + sustitución de placeholders `{{token}}`. |
| `links` | Inyección/actualización de wikilinks (Enlaces de proyecto, Tareas de ticket/iniciativa, agenda, "Trabajado hoy"). |
| `focus` | Lectura/escritura de `.focus`. Ejecutable para consulta. |
| `notes` | Append idempotente a la sección Notas con ancla `[[YYYYMMDD]]`. Ejecutable. |

## 4. Esquemas de datos (contratos)

### 4.1. Frontmatter por tipo de nota

Fuente de verdad del estado y la clasificación. Los `tags` se mantienen
**sincronizados** por script con los campos (doble representación: campos para
lógica/Dataview, tags para grafo/navegación). Org y proyecto en tags conservan
su capitalización (`Mango`, `Kondo`); el estado va en minúscula (`tarea/pendiente`).

**Tarea**
```yaml
type: task
status: pendiente          # pendiente | en-curso | bloqueada | terminada
ticket: ONLINE-173894      # o null si proviene de una iniciativa
initiative: null           # o nombre si proviene de una iniciativa
project: Kondo
org: Mango
created: 2026-06-25
done: null                 # fecha (AAAA-MM-DD) cuando pasa a terminada
tags: [Mango, Kondo, ONLINE-173894, tarea/pendiente]
```

**Ticket**
```yaml
type: ticket
id: ONLINE-173894
project: Kondo
org: Mango
tags: [Mango, Kondo, ONLINE-173894]
```

**Iniciativa**
```yaml
type: initiative
name: Adaptar Presentación
project: Charla Multiagentes
org: Capitole
tags: [Capitole, Charla Multiagentes, Adaptar Presentación]
```

**Reunión**
```yaml
type: meeting
date: 2026-06-25
project: Kondo
org: Mango
participants: [Agustín, ...]
tags: [Mango, Kondo]
```

**Proyecto**
```yaml
type: project
name: Kondo
org: Mango
tags: [Mango, Kondo]
```

**Organización**
```yaml
type: org
name: Mango
tags: [Mango]
```

**Nota diaria**
```yaml
type: daily
date: 2026-06-25
week: 2026-W26
tags: [daily]
```

> El motivo de bloqueo **no** va al frontmatter: se anota solo en la sección
> Notas de la tarea. Las conclusiones de tareas/reuniones son prosa y van solo
> al cuerpo.

### 4.2. Estado de foco — `.focus` (JSON)

```json
{
  "path": "Mango/Tickets/Tasks/ONLINE-173894_Buscar usos de las tablas.md",
  "type": "task",
  "day": "20260625",
  "since": "2026-06-25T10:14:00"
}
```

Ausencia del archivo o contenido vacío = **sin foco**. Tras terminar una
reunión, el foco queda vacío (no se restaura la tarea anterior).

### 4.3. Salida de los scripts (JSON + exit code)

Éxito (exit 0):
```json
{ "ok": true, "created": "Mango/Tickets/ONLINE-173894.md" }
```

Fallo (exit ≠ 0):
```json
{ "ok": false, "error": "La iniciativa 'Adaptar Presentación' no existe.", "code": "PARENT_NOT_FOUND" }
```

Ante `ok: false`, el agente muestra `error` al usuario, sugiere la skill de
remedio cuando aplique y **no** ejecuta acciones manuales. No hay log separado:
el propio vault (notas con timestamp) es la auditoría.

### 4.4. Salida de `now`

```json
{ "date": "20260625", "time": "10:14", "weekday": "thursday", "iso_week": "2026-W26", "is_friday": false }
```

### 4.5. Agenda parseada (LLM → script)

El agente parsea la agenda en lenguaje natural a este JSON, lo **confirma** con
el usuario y lo pasa al script `start_day.py`:

```json
{
  "start": "08:00",
  "end": "17:00",
  "breaks":   [ { "name": "Desayuno", "start": "10:00", "end": "10:30" } ],
  "meetings": [ { "name": "Kondo Daily", "start": "09:45", "end": "10:00" } ]
}
```

## 5. Catálogo de skills (14)

Una skill por acción ([ADR-0012](adr/0012-skills-granulares-focus-unificado.md)).
Prefijo `daily-flow-`.

| Comando | Pide | Script | Precondición | Efecto principal |
|---|---|---|---|---|
| `start-day` | agenda, prioridades | `start_day.py` | — (idempotente si ya existe) | Crea la nota diaria; Tasks por walk global; Agenda; Priorities; Trabajado hoy vacío |
| `end-day` | reflexión, tareas-mañana | `end_day.py` | daily del día existe | Escribe Day close out; si es viernes, ofrece `end-week` |
| `end-week` | prioridades semana | `end_week.py` | — | Recopila (lun-vie) → el agente redacta → escribe `W-NN.md` |
| `create-org` | nombre | `create_org.py` | — | Crea carpeta + nota de organización |
| `create-project` | nombre, org, descripción | `create_project.py` | org existe | Crea carpeta + nota de proyecto |
| `create-initiative` | nombre, proyecto, descripción | `create_initiative.py` | proyecto existe | Crea carpeta + nota; añade a Enlaces del proyecto |
| `create-ticket` | id, título, target, descripción, tareas | `create_ticket.py` | proyecto existe | Crea nota de ticket; añade a Enlaces del proyecto |
| `create-task` | título, descripción, ticket/iniciativa | `create_task.py` | ticket/iniciativa existe | Crea nota (estado pendiente); enlace bidireccional con el padre |
| `focus` | entidad | `focus.py` | daily del día existe | `.focus` → entidad; si es tarea, en-curso; ancla `[[día]]`; Trabajado hoy |
| `block-task` | motivo | `block_task.py` | foco = tarea | Motivo a Notas; tarea → bloqueada |
| `finish-task` | conclusiones | `finish_task.py` | foco = tarea | Conclusiones a Notas; tarea → terminada; `done` |
| `start-meeting` | reunión/ad-hoc, proyecto, participantes, goal | `start_meeting.py` | daily del día existe | Crea nota de reunión; wikilink en agenda; tarea en foco → pendiente; anida (cierra previa); Enlaces del proyecto; Trabajado hoy |
| `finish-meeting` | conclusiones | `finish_meeting.py` | foco = reunión | Conclusiones a la reunión; foco vacío |

> Focalizar organización o proyecto está **absorbido** por `focus` (foco
> unificado): cambia el destino de las notas, sin transición de estado.

## 6. Máquina de estados

Estados de tarea: `pendiente`, `en-curso`, `bloqueada`, `terminada` (terminal).
Las transiciones válidas y sus disparadores están en
[`especificacion-usuario.md`](especificacion-usuario.md#5-estados-de-una-tarea).
La validación es responsabilidad de `vault.tasks` (fuente de verdad);
`AGENTS.md` lleva un resumen en prosa para el razonamiento del agente.

Reglas operativas relevantes:

- `start-day` es idempotente: no sobrescribe una daily existente.
- `focus`, `block-task`, `finish-task`, `finish-meeting` validan precondiciones
  y fallan con mensaje claro si no se cumplen.
- Las reuniones **se anidan**: empezar una reunión con otra en foco cierra la
  anterior automáticamente (sin conclusiones, con una marca de cierre
  automático). Ver [ADR-0015](adr/0015-anidar-reuniones.md).

## 7. Plantillas

Ocho plantillas en `Templates/` con placeholders `{{token}}` (estilo mustache).
Las secciones aparecen con su encabezado y el cuerpo vacío; los scripts de
captura localizan el encabezado y hacen append. Las plantillas reales se usan
como entrada en los tests de integración (detectan roturas de relleno).

| Plantilla | Tipo |
|---|---|
| `daily_note.md` | nota diaria |
| `meeting.md` | reunión |
| `ticket.md` | ticket |
| `initiative.md` | iniciativa |
| `task.md` | tarea |
| `project.md` | proyecto |
| `org.md` | organización |
| `weekly_summary.md` | resumen semanal |

## 8. AGENTS.md

`auto_vault/AGENTS.md` es autocontenido en su dominio y define:

1. Rol del asistente (productividad diaria, captura estructurada).
2. **Regla de oro determinista**: nunca hacer a mano lo que puede un script; si
   falta el script, avisar y esperar.
3. Idioma del vault: español.
4. Enrutado de notas: texto libre → `vault.notes append` al foco actual; sin
   foco → nota diaria (con aviso único).
5. Invocación de scripts (rutas relativas a `cwd`).
6. Confirmación de datos parseados (agenda) antes de escribir.
7. Resumen de la FSM (estados, transiciones, efectos de foco/reunión).
8. Heurística **comando vs nota**: mensajes que empiezan por `/` o expresan una
   acción del sistema son comandos → invocar skill; el resto es nota → append.
   Ante ambigüedad, preguntar.
9. Mapa de skills disponibles y cuándo usar cada una.

## 9. Guía de desarrollo (TDD)

- **Método**: TDD estricto red-green-refactor. Ningún script se escribe sin un
  test que falle primero. Sin umbral numérico de cobertura (métrica informativa).
- **Pirámide**:
  - Lógica pura de `vault` (paths, markdown, FSM, fechas, plantillas, links) →
    **tests unitarios** sin tocar disco.
  - Orquestadores (que tocan el filesystem) → **tests de integración** con
    `tmp_path` (un vault temporal real, sembrado por un fixture que copia las
    plantillas reales).
- **Runner**: pytest, descubrimiento desde `.pi/skills/`:

  ```
  .pi/skills/.venv/bin/python -m pytest .pi/skills/
  ```

- **Añadir una skill nueva**: crear `daily-flow-<accion>/` con `SKILL.md`,
  `scripts/<x>.py` y `tests/test_<x>.py`; reutilizar `vault.*`; registrar la
  invocación en el `SKILL.md` y, si procede, en `AGENTS.md`.
- **Bootstrap**: ejecutar `./bootstrap.sh` una vez (requiere `uv`).
