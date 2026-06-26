"""Orquestador: cerrar el día.

Uso:
    python end_day.py --vault-root VAULT --day YYYYMMDD \
        --reflection TEXTO --pending JSON_LIST

JSON_LIST: ["basename_tarea1", …]

Precondición: debe existir la nota diaria del día.
Salida JSON (stdout) + exit code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vault import dates, markdown as md, paths
from vault.output import ok, fail
from datetime import datetime


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--day", required=True)
    parser.add_argument("--reflection", required=True)
    parser.add_argument("--pending", required=True)
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    day = args.day.strip()

    daily_path = vault / paths.daily_note(day)
    if not daily_path.exists():
        fail(f"No existe la nota diaria '{day}'. Lanza /daily-flow-start-day primero.", "NO_DAILY")

    try:
        pending = json.loads(args.pending)
    except json.JSONDecodeError as e:
        fail(f"JSON inválido en --pending: {e}", "INVALID_JSON")

    content = daily_path.read_text(encoding="utf-8")

    # Escribir reflexión
    content = md.append_to_section(content, "Day close out", f"**Reflexión**: {args.reflection}")

    # Escribir tareas pendientes para mañana
    if pending:
        content = md.append_to_section(content, "Day close out", "**Pendientes para mañana:**")
        for basename in pending:
            content = md.append_to_section(content, "Day close out", f"- [[{basename}]]")

    daily_path.write_text(content, encoding="utf-8")

    # Detectar si es viernes
    year, month, day_num = day[:4], day[4:6], day[6:]
    dt = datetime(int(year), int(month), int(day_num))
    is_fri = dates.is_friday(dt)

    ok(f"Día '{day}' cerrado.", is_friday=is_fri)


if __name__ == "__main__":
    main()
