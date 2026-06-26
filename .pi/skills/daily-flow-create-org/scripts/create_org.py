"""Orquestador: crear una organización en el vault.

Uso:
    python create_org.py --vault-root VAULT --name NOMBRE

Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from vault import paths, templates, markdown as md
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    raw_name = args.name.strip()

    # Sanear nombre para el sistema de archivos
    try:
        safe_name = paths.sanitize_filename(raw_name)
    except ValueError as e:
        fail(str(e), "INVALID_NAME")

    org_dir = vault / paths.org_dir(safe_name)
    note_path = vault / paths.org_note(safe_name)

    # Idempotente: si ya existe la nota, éxito sin sobrescribir
    if note_path.exists():
        ok(f"Organización '{safe_name}' ya existe.", path=str(note_path.relative_to(vault)))
        return

    tpl = vault / "Templates" / "org.md"
    context = {"name": safe_name}

    try:
        templates.copy_template(tpl, note_path, context)
    except FileNotFoundError as e:
        fail(str(e), "TEMPLATE_NOT_FOUND")
    except Exception as e:
        fail(str(e), "UNEXPECTED_ERROR")

    ok(f"Organización '{safe_name}' creada.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
