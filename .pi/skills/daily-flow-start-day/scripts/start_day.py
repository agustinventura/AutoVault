"""Orquestador: empezar el día — crea la nota diaria.

Uso:
    python start_day.py --vault-root VAULT --day YYYYMMDD \
        --agenda JSON --priorities JSON

JSON de agenda: {"start":"HH:MM","end":"HH:MM",
                  "breaks":[{"name":"…","start":"HH:MM","end":"HH:MM"}],
                  "meetings":[{"name":"…","start":"HH:MM","end":"HH:MM"}]}

JSON de prioridades: ["basename_tarea1", "basename_tarea2", …]  (hasta 3)

Salida JSON (stdout) + exit code.
Idempotente: si la nota del día ya existe, no la sobrescribe.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vault import dates, markdown as md, paths, tasks, templates
from vault.output import ok, fail


def _build_agenda_lines(agenda: dict) -> list[str]:
    """Construye las líneas de la sección Agenda ordenadas cronológicamente."""
    entries: list[tuple[str, str]] = []
    entries.append((agenda["start"], f"- {agenda['start']} Inicio de jornada"))
    for b in agenda.get("breaks", []):
        entries.append((b["start"], f"- {b['start']} - {b['end']} {b['name']}"))
    for m in agenda.get("meetings", []):
        entries.append((m["start"], f"- {m['start']} - {m['end']} {m['name']}"))
    entries.append((agenda["end"], f"- {agenda['end']} Fin de jornada"))
    entries.sort(key=lambda x: x[0])
    return [line for _, line in entries]


def _build_tasks_section(task_paths: list[Path], vault: Path) -> str:
    """Agrupa las tareas por estado y devuelve el texto de la sección Tasks."""
    by_status: dict[str, list[str]] = {"en-curso": [], "pendiente": [], "bloqueada": []}
    for tp in task_paths:
        content = (vault / tp).read_text(encoding="utf-8")
        status = md.get_field(content, "status")
        basename = paths.note_basename(tp)
        if status in by_status:
            by_status[status].append(f"- [[{basename}]]")
    lines = []
    for status, label in [("en-curso", "### En curso"), ("pendiente", "### Pendientes"), ("bloqueada", "### Bloqueadas")]:
        lines.append(label)
        lines.extend(by_status[status] or [""])
    return "\n".join(lines)


def _build_priorities_section(priorities: list[str], vault: Path) -> str:
    """Construye el texto de la sección Priorities con wikilinks + estado."""
    lines = []
    for basename in priorities[:3]:
        # Buscar el estado de la tarea
        status = _find_task_status(basename, vault)
        status_tag = f" (#tarea/{status})" if status else ""
        lines.append(f"- [[{basename}]]{status_tag}")
    return "\n".join(lines)


def _find_task_status(basename: str, vault: Path) -> str | None:
    for path in vault.rglob(f"{basename}.md"):
        if any(p.startswith(".") for p in path.parts):
            continue
        content = path.read_text(encoding="utf-8")
        if md.get_field(content, "type") == "task":
            return md.get_field(content, "status")
    return None


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--day", required=True)
    parser.add_argument("--agenda", required=True)
    parser.add_argument("--priorities", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    day = args.day.strip()

    try:
        agenda = json.loads(args.agenda)
        priorities = json.loads(args.priorities)
    except json.JSONDecodeError as e:
        fail(f"JSON inválido: {e}", "INVALID_JSON")

    note_path = vault / paths.daily_note(day)

    # Idempotente: si ya existe, retornar éxito sin sobrescribir
    if note_path.exists():
        ok(f"Nota diaria '{day}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    # Walk global de tareas activas
    active = tasks.find_tasks(vault, {"pendiente", "en-curso", "bloqueada"})

    # Construir secciones
    agenda_lines = _build_agenda_lines(agenda)
    tasks_text = _build_tasks_section(active, vault)
    priorities_text = _build_priorities_section(priorities, vault)

    # Calcular fecha de visualización: DD/MM/YYYY
    year, month, day_num = day[:4], day[4:6], day[6:]
    display_date = f"{day_num}/{month}/{year}"
    iso_date = f"{year}-{month}-{day_num}"

    from datetime import datetime
    dt = datetime(int(year), int(month), int(day_num))
    iso_w = dates.iso_week(dt)

    tpl = vault / "Templates" / "daily_note.md"
    context = {
        "date": iso_date,
        "iso_week": iso_w,
        "display_date": display_date,
        "work_start": agenda["start"],
        "work_end": agenda["end"],
        "agenda_items": "\n".join(
            line for line in agenda_lines
            if line.strip() not in (f"- {agenda['start']} Inicio de jornada",
                                    f"- {agenda['end']} Fin de jornada")
        ) + "\n",
        "priorities": priorities_text,
    }

    try:
        templates.copy_template(tpl, note_path, context)
    except Exception as e:
        fail(str(e), "TEMPLATE_ERROR")

    # Reemplazar la sección Tasks con el contenido real
    content = note_path.read_text(encoding="utf-8")
    content = md.replace_section(content, "Tasks", tasks_text)
    note_path.write_text(content, encoding="utf-8")

    ok(f"Nota diaria '{day}' creada.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
