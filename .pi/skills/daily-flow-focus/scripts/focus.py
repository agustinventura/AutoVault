"""Orquestador: focalizar una entidad del vault.

Uso:
    python focus.py --vault-root VAULT --path RUTA_RELATIVA --type TYPE \
        --day YYYYMMDD --time HH:MM --focus-file RUTA_FOCUS

TYPE: task | ticket | initiative | project | org | meeting

Precondición: debe existir la nota diaria del día (excepto para tipo meeting).
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from vault import focus as focus_mod, links, markdown as md, notes, paths, tasks
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--type", required=True, dest="type_")
    parser.add_argument("--day", required=True)
    parser.add_argument("--time", required=True)
    parser.add_argument("--focus-file", default=".focus")
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    rel_path = args.path.strip()
    type_ = args.type_.strip()
    day = args.day.strip()
    time = args.time.strip()
    focus_file = Path(args.focus_file)

    # Validar que la nota existe
    note_path = vault / rel_path
    if not note_path.exists():
        fail(f"La nota '{rel_path}' no existe.", "NOTE_NOT_FOUND")

    # Validar que existe la nota diaria
    daily_path = vault / paths.daily_note(day)
    if not daily_path.exists():
        fail(f"No existe la nota diaria '{day}'. Lanza /daily-flow-start-day primero.", "NO_DAILY")

    # Si es tarea, transición a en-curso
    if type_ == "task":
        content = note_path.read_text(encoding="utf-8")
        current_status = md.get_field(content, "status")
        if current_status != "en-curso":
            try:
                updated = tasks.set_status(content, "en-curso")
                note_path.write_text(updated, encoding="utf-8")
            except tasks.InvalidTransitionError as e:
                fail(str(e), "INVALID_TRANSITION")

        # Añadir ancla del día en Notas de la tarea (idempotente)
        content = note_path.read_text(encoding="utf-8")
        updated = notes.append_note(content, day=day, text="", section="Notas")
        # Solo insertar la ancla (sin bullet vacío): si ya está, no hacer nada
        if f"[[{day}]]" not in note_path.read_text(encoding="utf-8"):
            # Insertar solo el ancla
            section_body = md.get_section(content, "Notas")
            if f"[[{day}]]" not in section_body:
                content = md.append_to_section(content, "Notas", f"[[{day}]]")
                note_path.write_text(content, encoding="utf-8")

    # Actualizar "Trabajado hoy" en la daily
    basename = paths.note_basename(rel_path)
    daily_content = daily_path.read_text(encoding="utf-8")
    daily_updated = links.ensure_worked_today(daily_content, basename, time)
    daily_path.write_text(daily_updated, encoding="utf-8")

    # Escribir .focus
    focus_mod.write_focus(
        focus_file,
        path=rel_path,
        type_=type_,
        day=day,
        since=f"{day[:4]}-{day[4:6]}-{day[6:]}T{time}:00",
    )

    ok(f"Foco establecido en '{rel_path}'.", path=rel_path)


if __name__ == "__main__":
    main()
