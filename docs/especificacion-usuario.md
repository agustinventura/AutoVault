# Especificación de usuario — Asistente de productividad diaria

> Metodología de trabajo del asistente personal. Este documento describe **qué
> hace** el sistema y **cómo se usa**, sin detalles de implementación. Para la
> parte técnica, ver [`especificacion-tecnica.md`](especificacion-tecnica.md).

## 1. Propósito

Asistente de IA que actúa como secretario personal de un ingeniero de software.
Permite recopilar de forma fácil, rápida y estructurada las notas de las
reuniones y del trabajo técnico diario. La escritura se hace por consola
(agente conversacional); la lectura se hace con Obsidian, aprovechando
wikilinks, tags y el plugin Dataview.

Toda la información se guarda como Markdown dentro de un único directorio raíz
(el *vault*).

## 2. Conceptos

### 2.1. El día

Un **día** es una fecha en formato `YYYYMMDD` (por ejemplo `20260625`). Se
compone de horas de trabajo (por ejemplo de 8 a 17) divididas en **franjas**:

- **Descanso**: por ejemplo desayuno de 10:00 a 10:30, almuerzo de 13:30 a 14:30.
- **Reunión**: por ejemplo Kondo Daily de 9:45 a 10:00, Tribe Backend de 12 a 13.
- **Foco**: el resto del tiempo, dedicado a trabajar en tareas.

### 2.2. Jerarquía de trabajo

```
Organización  (Mango, Capitole)
└── Proyecto  (Kondo, Charla Multiagentes)
    ├── Ticket      (ONLINE-173894)  → trabajo formalizado en Jira/Linear/...
    │   └── Tarea   (actividad concreta)
    └── Iniciativa  (Adaptar Presentación)  → trabajo no formalizado
        └── Tarea   (actividad concreta)
```

- **Organización**: empresa o cliente para el que se trabaja.
- **Proyecto**: línea de trabajo dentro de una organización.
- **Ticket**: trabajo estructurado y trackeado en un sistema externo de
  ticketing. Su nombre es el ID del ticket.
- **Iniciativa**: trabajo de alto nivel **no** formalizado en un sistema
  externo.
- **Tarea**: actividad concreta a realizar, asociada a un ticket o a una
  iniciativa. Es una de las raíces del sistema: es lo que se "focaliza" para
  trabajar.
- **Reunión**: pertenece a un proyecto.

### 2.3. Foco

En cada momento hay (como mucho) **una** entidad en foco. Lo que el usuario
escribe en el agente se vuelca en la sección **Notas** de la entidad en foco.
Si no hay foco, se vuelca en la nota diaria (con un aviso).

Se puede focalizar cualquier entidad (tarea, ticket, iniciativa, proyecto,
organización). Solo focalizar una **tarea** tiene efecto sobre su estado (pasa
a *en curso*).

## 3. Estructura del vault

Rutas relativas al directorio raíz:

| Nota | Ruta | Ejemplo |
|---|---|---|
| Nota diaria | `Daily log/AAAA/MM/YYYYMMDD.md` | `Daily log/2026/06/20260625.md` |
| Resumen semanal | `Daily log/AAAA/MM/W-NN.md` | `Daily log/2026/06/W-26.md` |
| Organización | `<Org>/<Org>.md` | `Mango/Mango.md` |
| Reunión | `<Org>/Meetings/AAAA/MM/YYYYMMDD-<Nombre>.md` | `Mango/Meetings/2026/06/20260625-Tribe Backend.md` |
| Proyecto | `<Org>/Proyectos/<Proyecto>/<Proyecto>.md` | `Mango/Proyectos/Kondo/Kondo.md` |
| Ticket | `<Org>/Tickets/<ID>.md` | `Mango/Tickets/ONLINE-173894.md` |
| Tarea de ticket | `<Org>/Tickets/Tasks/<ID>_<Título>.md` | `Mango/Tickets/Tasks/ONLINE-173894_Buscar usos de las tablas.md` |
| Iniciativa | `<Org>/Proyectos/<Proyecto>/Iniciativas/<Iniciativa>/<Iniciativa>.md` | `Capitole/Proyectos/Charla Multiagentes/Iniciativas/Adaptar Presentación/Adaptar Presentación.md` |
| Tarea de iniciativa | `…/Iniciativas/<Iniciativa>/Tasks/<Título>.md` | `…/Adaptar Presentación/Tasks/Acortar presentación.md` |

Las organizaciones también pueden contener notas sueltas (por ejemplo
`Información Básica.md`, `Enlaces.md`).

> **Nota sobre nombres de tarea**: la asimetría es intencional. Las tareas de
> ticket llevan el prefijo del ID (`ONLINE-173894_…`) porque comparten carpeta
> `Tickets/Tasks/` y podrían colisionar; las tareas de iniciativa viven en la
> carpeta propia de su iniciativa, donde no colisionan.

## 4. Secciones de cada nota

### Nota diaria — `Diario del DD/MM/YYYY`
- **Agenda**: hora de inicio, reuniones (con su horario) y hora de fin,
  ordenada cronológicamente.
- **Tasks**: todas las tareas pendientes, en curso o bloqueadas **a día de
  hoy**, agrupadas por estado.
- **Priorities**: hasta tres tareas principales del día, con su estado actual.
- **Notes**: texto libre del día (apuntes no estructurados).
- **Trabajado hoy**: entidades focalizadas durante el día (con la hora del
  primer foco).
- **Day close out**: reflexión del día y tareas pendientes para el día
  siguiente.

### Reunión — `<Fecha> <Nombre>`
- **Goal**: descripción breve de lo que se pretende.
- **Participants**: lista de participantes.
- **Notas**: notas tomadas durante la reunión.
- **Conclusiones**: recapitulación y conclusiones.

### Ticket — `<ID> <Descripción>`
- **Target**: objetivo una vez clarificado.
- **Description**: descripción **tal y como** aparece en el sistema de ticketing.
- **Tareas**: lista de las tareas del ticket.
- **Notas**: por cada día trabajado, un enlace a la nota diaria y las anotaciones.

### Iniciativa — `<Nombre>`
- **Description**: descripción de la iniciativa.
- **Tareas**: lista de las tareas de la iniciativa.
- **Notas**: por cada día trabajado, un enlace a la nota diaria y las anotaciones.

### Tarea — `<Título>`
- **Description**: descripción de la tarea.
- **Notas**: por cada día trabajado, un enlace a la nota diaria y la información
  técnica relevante.

### Proyecto — `<Nombre>`
- **Description**: descripción del proyecto.
- **Enlaces**: enlaces a las reuniones, iniciativas y tickets del proyecto.

### Organización — `<Nombre>`
- Cuerpo libre.

## 5. Estados de una tarea

Una tarea tiene uno de cuatro estados:

- `pendiente`
- `en-curso`
- `bloqueada`
- `terminada` (terminal)

### Transiciones válidas

```
pendiente ──focus──▶ en-curso ──finish──▶ terminada
    ▲                  │  │
    │                  │  └──block──▶ bloqueada ──focus──▶ en-curso
    └── start-meeting ─┘                   └──finish──▶ terminada
   (si estaba en foco)
```

- De **pendiente** → en-curso (al focalizarla).
- De **en-curso** → pendiente (si se empieza una reunión teniéndola en foco),
  bloqueada (al bloquearla) o terminada (al terminarla).
- De **bloqueada** → en-curso (al focalizarla) o terminada (al terminarla).
- **terminada** es terminal.

## 6. Flujo de un día

### Empezar el día
1. El asistente obtiene la fecha actual.
2. Pregunta la agenda (horario, descansos, reuniones).
3. Lista todas las tareas pendientes, en curso y bloqueadas.
4. Pregunta las prioridades (hasta tres).
5. Crea la nota diaria con toda esa información.

### Durante el día
- **Focalizar** un ticket, iniciativa o tarea: lo que se escriba a continuación
  se vuelca en la sección Notas de esa nota. Focalizar una tarea la pone *en
  curso*. La primera vez que se trabaja una entidad en el día, se enlaza la nota
  diaria (`[[YYYYMMDD]]`).
- **Crear** una tarea, ticket, iniciativa, proyecto u organización nuevos.
- **Bloquear** la tarea en foco: pide un motivo (se anota en sus Notas) y la
  marca como bloqueada.
- **Terminar** la tarea en foco: pide conclusiones y la marca como terminada.
- **Empezar una reunión**: se elige una de la agenda (o se crea una nueva
  ad-hoc, que se inserta en la agenda con la hora actual). Si había una tarea en
  foco, pasa a pendiente. Todo lo que se anote va a las Notas de la reunión.
- **Terminar una reunión**: pide conclusiones. El foco queda vacío; hay que
  volver a focalizar para continuar.

### Terminar el día
1. Pide una reflexión del día (se anota en Day close out).
2. Pide las tareas pendientes para el día siguiente.
3. Si es viernes, ofrece generar el resumen semanal.

## 7. Fin de la semana

Los viernes, al terminar el día, el asistente ofrece generar un **resumen
semanal** en `Daily log/AAAA/MM/W-NN.md` (numeración ISO de semana, recopilando
de lunes a viernes), con:

- **Tareas completadas** durante la semana.
- **Resumen del trabajo en tickets**.
- **Resumen del trabajo en iniciativas**.
- **Prioridades para la semana que viene** (se preguntan al usuario tras
  presentar lo anterior).

## 8. Reglas de comportamiento

- Lo que el usuario escribe se interpreta como **nota** (se vuelca a la entidad
  en foco) salvo que sea un **comando** (acción del sistema: empezar/terminar
  reunión, focalizar, bloquear, terminar, etc.).
- Sin foco activo, las notas van a la nota diaria del día.
- Para focalizar o tomar notas debe existir la nota diaria del día: si no, hay
  que empezar el día primero. Crear entidades (organizaciones, proyectos,
  tickets, iniciativas, tareas) es independiente del día.
- El contenido del vault se redacta en español.
