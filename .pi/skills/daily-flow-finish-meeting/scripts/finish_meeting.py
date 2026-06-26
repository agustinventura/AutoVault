"""Orquestador: terminar la reunión en foco.

Uso:
    python finish_meeting.py --vault-root VAULT --focus-file FOCUS \
        --conclusion TEXTO

Precondición: .focus debe apuntar a una reunión.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from vault import focus as focus_mod, markdown as md
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--focus-file", default=".focus")
    parser.add_argument("--conclusion", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    focus_file = Path(args.focus_file)

    data = focus_mod.read_focus(focus_file)
    if not data or data.get("type") != "meeting":
        fail("No hay reunión en foco. Usa /daily-flow-start-meeting primero.", "NO_MEETING_FOCUS")

    note_path = vault / data["path"]
    if not note_path.exists():
        fail(f"La nota '{data['path']}' no existe.", "NOTE_NOT_FOUND")

    content = note_path.read_text(encoding="utf-8")
    updated = md.append_to_section(content, "Conclusiones", args.conclusion)
    note_path.write_text(updated, encoding="utf-8")

    # Limpiar el foco
    focus_mod.clear_focus(focus_file)

    ok(f"Reunión terminada: {data['path']}")


if __name__ == "__main__":
    main()
