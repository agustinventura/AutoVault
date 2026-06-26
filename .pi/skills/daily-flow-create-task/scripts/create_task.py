"""Orquestador: crear una tarea en el vault.

Uso (desde ticket):
    python create_task.py --vault-root VAULT --org ORG --ticket TICKET_ID \
        --title TITULO --description DESC

Uso (desde iniciativa):
    python create_task.py --vault-root VAULT --org ORG --project PROJECT \
        --initiative NOMBRE --title TITULO --description DESC

Precondición: el padre (ticket o iniciativa) debe existir.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from vault import paths, templates, markdown as md, links
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--org", required=True)
    parser.add_argument("--ticket", default=None)
    parser.add_argument("--initiative", default=None)
    parser.add_argument("--project", default=None)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    org = args.org.strip()
    title = args.title.strip()
    description = args.description.strip()

    if args.ticket:
        _create_from_ticket(vault, org, args.ticket.strip(), title, description)
    elif args.initiative and args.project:
        _create_from_initiative(
            vault, org, args.project.strip(), args.initiative.strip(), title, description
        )
    else:
        fail("Debe especificar --ticket o --initiative + --project.", "MISSING_PARENT")


def _create_from_ticket(vault: Path, org: str, ticket_id: str, title: str, desc: str):
    ticket_note_path = vault / paths.ticket_note(org, ticket_id)
    if not ticket_note_path.exists():
        fail(f"El ticket '{ticket_id}' no existe en '{org}'.", "PARENT_NOT_FOUND")

    note_path = vault / paths.ticket_task_note(org, ticket_id, title)
    if note_path.exists():
        ok(f"Tarea '{title}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    # Obtener el proyecto desde el frontmatter del ticket
    ticket_content = ticket_note_path.read_text(encoding="utf-8")
    project = md.get_field(ticket_content, "project") or ""

    tpl = vault / "Templates" / "task.md"
    context = {
        "title": title,
        "description": desc,
        "org": org,
        "project": project,
        "ticket": ticket_id,
        "initiative": "null",
        "parent_id": ticket_id,
        "created": str(date.today()),
    }
    templates.copy_template(tpl, note_path, context)

    # Enlace bidireccional: añadir la tarea a "Tareas" del ticket
    updated = links.ensure_link_in_section(
        ticket_note_path.read_text(encoding="utf-8"),
        "Tareas",
        paths.note_basename(note_path),
    )
    ticket_note_path.write_text(updated, encoding="utf-8")

    ok(f"Tarea '{title}' creada.", path=str(note_path.relative_to(vault)))


def _create_from_initiative(
    vault: Path, org: str, project: str, initiative: str, title: str, desc: str
):
    init_note_path = vault / paths.initiative_note(org, project, initiative)
    if not init_note_path.exists():
        fail(f"La iniciativa '{initiative}' no existe.", "PARENT_NOT_FOUND")

    note_path = vault / paths.initiative_task_note(org, project, initiative, title)
    if note_path.exists():
        ok(f"Tarea '{title}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    tpl = vault / "Templates" / "task.md"
    context = {
        "title": title,
        "description": desc,
        "org": org,
        "project": project,
        "ticket": "null",
        "initiative": initiative,
        "parent_id": initiative,
        "created": str(date.today()),
    }
    templates.copy_template(tpl, note_path, context)

    # Enlace bidireccional: añadir la tarea a "Tareas" de la iniciativa
    updated = links.ensure_link_in_section(
        init_note_path.read_text(encoding="utf-8"),
        "Tareas",
        paths.note_basename(note_path),
    )
    init_note_path.write_text(updated, encoding="utf-8")

    ok(f"Tarea '{title}' creada.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
