"""Orquestador: terminar la tarea en foco.

Uso:
    python finish_task.py --vault-root VAULT --focus-file FOCUS \
        --conclusion TEXTO --day YYYYMMDD --time HH:MM

Precondición: .focus debe apuntar a una tarea.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from vault import focus as focus_mod, markdown as md, notes, tasks
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--focus-file", default=".focus")
    parser.add_argument("--conclusion", required=True)
    parser.add_argument("--day", required=True)
    parser.add_argument("--time", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    focus_file = Path(args.focus_file)

    data = focus_mod.read_focus(focus_file)
    if not data or data.get("type") != "task":
        fail("No hay tarea en foco. Usa /daily-flow-focus primero.", "NO_TASK_FOCUS")

    note_path = vault / data["path"]
    if not note_path.exists():
        fail(f"La nota '{data['path']}' no existe.", "NOTE_NOT_FOUND")

    content = note_path.read_text(encoding="utf-8")
    done_date = str(date.today())
    try:
        updated = tasks.set_status(content, "terminada", done_date=done_date)
    except tasks.InvalidTransitionError as e:
        fail(str(e), "INVALID_TRANSITION")

    # Anotar conclusión en Notas
    conclusion_line = f"- {args.time} **Conclusión**: {args.conclusion}"
    updated = notes.append_note(updated, day=args.day, text=conclusion_line)
    note_path.write_text(updated, encoding="utf-8")

    # Limpiar el foco
    focus_mod.clear_focus(focus_file)

    ok(f"Tarea terminada: {data['path']}", done=done_date)


if __name__ == "__main__":
    main()
