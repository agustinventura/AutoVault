"""Orquestador: crear un ticket en el vault.

Uso:
    python create_ticket.py --vault-root VAULT --org ORG --project PROJECT \
        --id ID --title TITLE --target TARGET --description DESC

Precondición: org y proyecto deben existir.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from vault import paths, templates, markdown as md, links
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--org", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    org = args.org.strip()
    project = args.project.strip()
    ticket_id = args.id.strip()

    # Validar org
    if not (vault / paths.org_note(org)).exists():
        fail(f"La organización '{org}' no existe.", "ORG_NOT_FOUND")

    # Validar proyecto
    if not (vault / paths.project_note(org, project)).exists():
        fail(f"El proyecto '{project}' no existe en '{org}'.", "PROJECT_NOT_FOUND")

    note_path = vault / paths.ticket_note(org, ticket_id)

    # Idempotente
    if note_path.exists():
        ok(f"Ticket '{ticket_id}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    tpl = vault / "Templates" / "ticket.md"
    context = {
        "id": ticket_id,
        "title": args.title.strip(),
        "target": args.target.strip(),
        "description": args.description.strip(),
        "org": org,
        "project": project,
    }

    try:
        templates.copy_template(tpl, note_path, context)
    except FileNotFoundError as e:
        fail(str(e), "TEMPLATE_NOT_FOUND")
    except Exception as e:
        fail(str(e), "UNEXPECTED_ERROR")

    # Enlace bidireccional: añadir wikilink del ticket a la sección
    # "Enlaces" del proyecto
    project_note_path = vault / paths.project_note(org, project)
    project_content = project_note_path.read_text(encoding="utf-8")
    updated = links.ensure_link_in_section(project_content, "Enlaces", ticket_id)
    project_note_path.write_text(updated, encoding="utf-8")

    ok(f"Ticket '{ticket_id}' creado.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
