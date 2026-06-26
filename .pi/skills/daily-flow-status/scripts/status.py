"""Orquestador: estado del foco actual.

Uso:
    python status.py --vault-root VAULT [--focus-file FOCUS]

Salida JSON:
  Sin foco:  {"ok": true, "focused": false}
  Con foco:  {"ok": true, "focused": true, "path": "…", "type": "…",
               "day": "YYYYMMDD", "since": "…", "task_status": "…"|null}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vault import focus as focus_mod, markdown as md
from vault.output import ok


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--focus-file", default=".focus")
    args = parser.parse_args(argv)

    vault = Path(args.vault_root)
    focus_file = Path(args.focus_file)

    data = focus_mod.read_focus(focus_file)

    if not data:
        print(json.dumps({"ok": True, "focused": False}, ensure_ascii=False))
        return

    result: dict = {
        "ok": True,
        "focused": True,
        "path": data["path"],
        "type": data["type"],
        "day": data["day"],
        "since": data.get("since"),
    }

    # Si es tarea, incluir el estado actual desde el frontmatter
    if data["type"] == "task":
        note_path = vault / data["path"]
        if note_path.exists():
            content = note_path.read_text(encoding="utf-8")
            result["task_status"] = md.get_field(content, "status")

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
