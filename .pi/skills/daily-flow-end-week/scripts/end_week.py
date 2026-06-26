"""Orquestador: generar el resumen semanal.

Uso:
    python end_week.py --vault-root VAULT --day YYYYMMDD \
        --week-label W-NN --iso-week AAAA-Www \
        --date-from AAAA-MM-DD --date-to AAAA-MM-DD \
        --completed-tasks JSON_LIST \
        --tickets-summary TEXTO \
        --initiatives-summary TEXTO \
        --priorities JSON_LIST

El LLM recopila datos y redacta los resúmenes; este script solo escribe.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vault import markdown as md, paths, templates
from vault.output import ok, fail


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--day", required=True)
    parser.add_argument("--week-label", required=True)
    parser.add_argument("--iso-week", required=True)
    parser.add_argument("--date-from", required=True)
    parser.add_argument("--date-to", required=True)
    parser.add_argument("--completed-tasks", required=True)
    parser.add_argument("--tickets-summary", required=True)
    parser.add_argument("--initiatives-summary", required=True)
    parser.add_argument("--priorities", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    day = args.day.strip()
    week_label = args.week_label.strip()

    try:
        completed = json.loads(args.completed_tasks)
        priorities = json.loads(args.priorities)
    except json.JSONDecodeError as e:
        fail(f"JSON inválido: {e}", "INVALID_JSON")

    note_path = vault / paths.weekly_summary(day, week_label)

    tpl = vault / "Templates" / "weekly_summary.md"
    context = {
        "week_label": week_label,
        "iso_week": args.iso_week,
        "date_from": args.date_from,
        "date_to": args.date_to,
    }

    try:
        templates.copy_template(tpl, note_path, context, overwrite=True)
    except Exception as e:
        fail(str(e), "TEMPLATE_ERROR")

    content = note_path.read_text(encoding="utf-8")

    # Tareas completadas
    if completed:
        for task in completed:
            content = md.append_to_section(content, "Tareas completadas", f"- {task}")

    # Resumen tickets
    content = md.append_to_section(content, "Resumen del trabajo en tickets",
                                    args.tickets_summary)

    # Resumen iniciativas
    content = md.append_to_section(content, "Resumen del trabajo en iniciativas",
                                    args.initiatives_summary)

    # Prioridades
    for p in priorities:
        content = md.append_to_section(content, "Prioridades para la semana que viene",
                                        f"- {p}")

    note_path.write_text(content, encoding="utf-8")
    ok(f"Resumen semanal '{week_label}' generado.", path=str(note_path.relative_to(vault)))


if __name__ == "__main__":
    main()
