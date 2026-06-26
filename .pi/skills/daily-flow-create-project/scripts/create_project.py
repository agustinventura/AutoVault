"""Orquestador: crear un proyecto en el vault.

Uso:
    python create_project.py --vault-root VAULT --org ORG --name NOMBRE --description DESC

Precondición: la organización debe existir.
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
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    org = args.org.strip()
    raw_name = args.name.strip()
    description = args.description.strip()

    # Validar org existente
    org_note = vault / paths.org_note(org)
    if not org_note.exists():
        fail(f"La organización '{org}' no existe. Créala primero con /daily-flow-create-org.", "ORG_NOT_FOUND")

    try:
        safe_name = paths.sanitize_filename(raw_name)
    except ValueError as e:
        fail(str(e), "INVALID_NAME")

    note_path = vault / paths.project_note(org, safe_name)

    # Idempotente
    if note_path.exists():
        ok(f"Proyecto '{safe_name}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    tpl = vault / "Templates" / "project.md"
    context = {
        "name": safe_name,
        "org": org,
        "description": description,
    }

    try:
        templates.copy_template(tpl, note_path, context)
    except FileNotFoundError as e:
        fail(str(e), "TEMPLATE_NOT_FOUND")
    except Exception as e:
        fail(str(e), "UNEXPECTED_ERROR")

    ok(f"Proyecto '{safe_name}' creado.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
