"""Orquestador: empezar una reunión.

Uso (reunión con nota propia):
    python start_meeting.py --vault-root VAULT --day YYYYMMDD --time HH:MM \
        --org ORG --project PROJECT --name NOMBRE \
        --participants TEXTO --goal TEXTO --focus-file FOCUS [--ad-hoc]

Uso (reunión inline — notas en la daily):
    ... mismo + --inline

Con --inline no se crea nota propia; las notas van a la sección
## NOMBRE dentro de Notes de la nota diaria.

Precondición: debe existir la nota diaria.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from vault import focus as focus_mod, links, markdown as md, notes, paths, tasks, templates
from vault.output import ok, fail


def _transition_task_to_pendiente(vault: Path, current_focus: dict) -> None:
    """Si hay tarea en foco, la pasa a pendiente (ignora si ya terminada/bloqueada)."""
    if current_focus.get("type") != "task":
        return
    task_note_path = vault / current_focus["path"]
    if not task_note_path.exists():
        return
    task_content = task_note_path.read_text(encoding="utf-8")
    try:
        updated = tasks.set_status(task_content, "pendiente")
        task_note_path.write_text(updated, encoding="utf-8")
    except tasks.InvalidTransitionError:
        pass


def _autoclose_meeting(vault: Path, current_focus: dict, new_meeting_name: str,
                        org: str, day: str) -> None:
    """Cierra automáticamente una reunión previa (con nota propia) sin conclusiones."""
    if current_focus.get("type") != "meeting":
        return
    prev_note_path = vault / current_focus["path"]
    if not prev_note_path.exists():
        return
    meeting_basename = paths.note_basename(paths.meeting_note(org, day, new_meeting_name))
    auto_close_msg = f"*Reunión cerrada automáticamente al iniciar [[{meeting_basename}]]*"
    prev_content = prev_note_path.read_text(encoding="utf-8")
    prev_updated = md.append_to_section(prev_content, "Conclusiones", auto_close_msg)
    prev_note_path.write_text(prev_updated, encoding="utf-8")


def _insert_in_agenda(daily_content: str, name: str, time: str,
                       label: str, ad_hoc: bool) -> str:
    """Inserta o inyecta la reunión en la sección Agenda."""
    if ad_hoc:
        return links.insert_meeting_line(daily_content, time, label)
    try:
        return links.inject_meeting_wikilink(daily_content, name, label)
    except KeyError:
        return links.insert_meeting_line(daily_content, time, label)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--day", required=True)
    parser.add_argument("--time", required=True)
    parser.add_argument("--org", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--participants", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--focus-file", default=".focus")
    parser.add_argument("--ad-hoc", action="store_true",
                        help="La reunión no estaba en la agenda; se inserta")
    parser.add_argument("--inline", action="store_true",
                        help="Sin nota propia; las notas van a la sección ## Nombre en Notes de la daily")
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    day = args.day.strip()
    time = args.time.strip()
    org = args.org.strip()
    project = args.project.strip()
    name = args.name.strip()
    focus_file = Path(args.focus_file)
    year, month, day_num = day[:4], day[4:6], day[6:]

    # Validar daily
    daily_path = vault / paths.daily_note(day)
    if not daily_path.exists():
        fail(f"No existe la nota diaria '{day}'. Lanza /daily-flow-start-day primero.", "NO_DAILY")

    # Validar org y proyecto
    if not (vault / paths.org_note(org)).exists():
        fail(f"La organización '{org}' no existe.", "ORG_NOT_FOUND")
    if not (vault / paths.project_note(org, project)).exists():
        fail(f"El proyecto '{project}' no existe.", "PROJECT_NOT_FOUND")

    # Gestión del foco previo
    current_focus = focus_mod.read_focus(focus_file)
    if current_focus:
        _autoclose_meeting(vault, current_focus, name, org, day)
        _transition_task_to_pendiente(vault, current_focus)

    if args.inline:
        _start_inline(vault, daily_path, day, time, year, month, day_num,
                      org, project, name, args, focus_file)
    else:
        _start_with_note(vault, daily_path, day, time, year, month, day_num,
                         org, project, name, args, focus_file)


def _start_inline(vault, daily_path, day, time, year, month, day_num,
                  org, project, name, args, focus_file):
    """Reunión sin nota propia: notas en subsección ## Nombre dentro de Notes."""
    daily_content = daily_path.read_text(encoding="utf-8")

    # Insertar subsección ### Nombre en Notes si no existe
    section_header = f"### {name}"
    notes_body = md.get_section(daily_content, "Notes")
    if section_header not in notes_body:
        daily_content = md.append_to_section(daily_content, "Notes", section_header)

    # Agenda: texto plano (sin wikilink para inline)
    agenda_label = f"{name} (inline)"
    daily_content = _insert_in_agenda(daily_content, name, time, name, args.ad_hoc)

    # Trabajado hoy
    daily_content = links.ensure_worked_today(daily_content, name, time)
    daily_path.write_text(daily_content, encoding="utf-8")

    # Foco: apunta a la daily con section = nombre de la reunión
    daily_rel = str(paths.daily_note(day))
    focus_mod.write_focus(
        focus_file,
        path=daily_rel,
        type_="inline-meeting",
        day=day,
        since=f"{year}-{month}-{day_num}T{time}:00",
        section=name,
    )

    ok(f"Reunión inline '{name}' iniciada en la daily.", path=daily_rel, inline=True)


def _start_with_note(vault, daily_path, day, time, year, month, day_num,
                     org, project, name, args, focus_file):
    """Reunión con nota propia."""
    meeting_note_path = vault / paths.meeting_note(org, day, name)
    meeting_note_path.parent.mkdir(parents=True, exist_ok=True)

    tpl = vault / "Templates" / "meeting.md"
    date_display = f"{day_num}/{month}/{year}"
    iso_date = f"{year}-{month}-{day_num}"
    participants_list = "\n".join(f"- {p.strip()}" for p in args.participants.split(","))

    context = {
        "date": iso_date,
        "date_display": date_display,
        "title": name,
        "org": org,
        "project": project,
        "participants": args.participants,
        "participants_list": participants_list,
        "goal": args.goal,
    }

    if not meeting_note_path.exists():
        try:
            templates.copy_template(tpl, meeting_note_path, context)
        except Exception as e:
            fail(str(e), "TEMPLATE_ERROR")

    meeting_basename = paths.note_basename(meeting_note_path)
    daily_content = daily_path.read_text(encoding="utf-8")

    # Agenda (wikilink)
    daily_updated = _insert_in_agenda(daily_content, name, time,
                                       f"[[{meeting_basename}]]", args.ad_hoc)

    # Trabajado hoy
    daily_updated = links.ensure_worked_today(daily_updated, meeting_basename, time)
    daily_path.write_text(daily_updated, encoding="utf-8")

    # Enlace en proyecto
    project_note_path = vault / paths.project_note(org, project)
    project_content = project_note_path.read_text(encoding="utf-8")
    project_updated = links.ensure_link_in_section(project_content, "Enlaces", meeting_basename)
    project_note_path.write_text(project_updated, encoding="utf-8")

    # Foco
    focus_mod.write_focus(
        focus_file,
        path=str(paths.meeting_note(org, day, name)),
        type_="meeting",
        day=day,
        since=f"{year}-{month}-{day_num}T{time}:00",
    )

    ok(f"Reunión '{name}' iniciada.", path=str(meeting_note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
