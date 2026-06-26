"""Orquestador: crear una iniciativa en el vault.

Uso:
    python create_initiative.py --vault-root VAULT --org ORG --project PROJECT \
        --name NOMBRE --description DESC

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
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    org = args.org.strip()
    project = args.project.strip()
    raw_name = args.name.strip()

    # Validar org
    if not (vault / paths.org_note(org)).exists():
        fail(f"La organización '{org}' no existe.", "ORG_NOT_FOUND")

    # Validar proyecto
    if not (vault / paths.project_note(org, project)).exists():
        fail(f"El proyecto '{project}' no existe en '{org}'.", "PROJECT_NOT_FOUND")

    try:
        safe_name = paths.sanitize_filename(raw_name)
    except ValueError as e:
        fail(str(e), "INVALID_NAME")

    note_path = vault / paths.initiative_note(org, project, safe_name)

    # Idempotente
    if note_path.exists():
        ok(f"Iniciativa '{safe_name}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    tpl = vault / "Templates" / "initiative.md"
    context = {
        "name": safe_name,
        "org": org,
        "project": project,
        "description": args.description.strip(),
    }

    try:
        templates.copy_template(tpl, note_path, context)
    except FileNotFoundError as e:
        fail(str(e), "TEMPLATE_NOT_FOUND")
    except Exception as e:
        fail(str(e), "UNEXPECTED_ERROR")

    # Enlace bidireccional: añadir wikilink de la iniciativa al proyecto
    project_note_path = vault / paths.project_note(org, project)
    project_content = project_note_path.read_text(encoding="utf-8")
    updated = links.ensure_link_in_section(project_content, "Enlaces", safe_name)
    project_note_path.write_text(updated, encoding="utf-8")

    ok(f"Iniciativa '{safe_name}' creada.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
