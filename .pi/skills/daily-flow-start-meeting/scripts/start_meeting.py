"""Orquestador: empezar una reunión.

Uso:
    python start_meeting.py --vault-root VAULT --day YYYYMMDD --time HH:MM \
        --org ORG --project PROJECT --name NOMBRE \
        --participants TEXTO --goal TEXTO --focus-file FOCUS [--ad-hoc]

Precondición: debe existir la nota diaria.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from vault import focus as focus_mod, links, markdown as md, notes, paths, tasks, templates
from vault.output import ok, fail


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
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    day = args.day.strip()
    time = args.time.strip()
    org = args.org.strip()
    project = args.project.strip()
    name = args.name.strip()
    focus_file = Path(args.focus_file)

    # Validar daily
    daily_path = vault / paths.daily_note(day)
    if not daily_path.exists():
        fail(f"No existe la nota diaria '{day}'. Lanza /daily-flow-start-day primero.", "NO_DAILY")

    # Validar org y proyecto
    if not (vault / paths.org_note(org)).exists():
        fail(f"La organización '{org}' no existe.", "ORG_NOT_FOUND")
    if not (vault / paths.project_note(org, project)).exists():
        fail(f"El proyecto '{project}' no existe.", "PROJECT_NOT_FOUND")

    # Si hay reunión previa en foco, cerrarla automáticamente (anidación A1)
    current_focus = focus_mod.read_focus(focus_file)
    if current_focus and current_focus.get("type") == "meeting":
        prev_note_path = vault / current_focus["path"]
        if prev_note_path.exists():
            prev_content = prev_note_path.read_text(encoding="utf-8")
            prev_name = paths.note_basename(current_focus["path"])
            meeting_basename = paths.note_basename(paths.meeting_note(org, day, name))
            auto_close_msg = f"*Reunión cerrada automáticamente al iniciar [[{meeting_basename}]]*"
            prev_updated = md.append_to_section(prev_content, "Conclusiones", auto_close_msg)
            prev_note_path.write_text(prev_updated, encoding="utf-8")

    # Si hay tarea en foco, pasarla a pendiente
    if current_focus and current_focus.get("type") == "task":
        task_note_path = vault / current_focus["path"]
        if task_note_path.exists():
            task_content = task_note_path.read_text(encoding="utf-8")
            try:
                updated = tasks.set_status(task_content, "pendiente")
                task_note_path.write_text(updated, encoding="utf-8")
            except tasks.InvalidTransitionError:
                pass  # Si ya estaba en otro estado, ignorar

    # Crear nota de la reunión
    meeting_note_path = vault / paths.meeting_note(org, day, name)
    meeting_note_path.parent.mkdir(parents=True, exist_ok=True)

    tpl = vault / "Templates" / "meeting.md"
    year, month, day_num = day[:4], day[4:6], day[6:]
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

    # Inyectar wikilink en la agenda de la daily (W3)
    meeting_basename = paths.note_basename(meeting_note_path)
    daily_content = daily_path.read_text(encoding="utf-8")

    if args.ad_hoc:
        # Insertar nueva línea en la agenda con la hora actual y el wikilink
        daily_updated = links.insert_meeting_line(
            daily_content, time, f"[[{meeting_basename}]]"
        )
    else:
        # Reemplazar la línea existente con el wikilink (L2)
        try:
            daily_updated = links.inject_meeting_wikilink(
                daily_content, name, meeting_basename
            )
        except KeyError:
            # Si no está en la agenda (se añadió ad-hoc de todas formas)
            daily_updated = links.insert_meeting_line(
                daily_content, time, f"[[{meeting_basename}]]"
            )

    # Añadir a "Trabajado hoy"
    daily_updated = links.ensure_worked_today(daily_updated, meeting_basename, time)
    daily_path.write_text(daily_updated, encoding="utf-8")

    # Añadir wikilink al proyecto (Enlaces)
    project_note_path = vault / paths.project_note(org, project)
    project_content = project_note_path.read_text(encoding="utf-8")
    project_updated = links.ensure_link_in_section(
        project_content, "Enlaces", meeting_basename
    )
    project_note_path.write_text(project_updated, encoding="utf-8")

    # Establecer foco en la reunión
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
