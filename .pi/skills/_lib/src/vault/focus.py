"""Lectura y escritura del archivo de estado ``.focus``.

El archivo es un JSON con ``{path, type, day, since[, section]}``.
El campo ``section`` es opcional; se usa en reuniones inline para indicar
la subsección de la nota diaria donde se acumulan las notas (p. ej. ``"Kondo Daily"``).
Ausencia o vacío = sin foco.

Ejecutable:
    python -m vault.focus get [--focus-file PATH]
"""

from __future__ import annotations

import json
from pathlib import Path


_FOCUS_FILE = Path(".focus")


def read_focus(focus_file: Path = _FOCUS_FILE) -> dict | None:
    """Lee el estado de foco. Devuelve ``None`` si no hay foco activo."""
    if not focus_file.exists():
        return None
    raw = focus_file.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    return json.loads(raw)


def write_focus(
    focus_file: Path = _FOCUS_FILE,
    *,
    path: str,
    type_: str,
    day: str,
    since: str,
    section: str | None = None,
) -> None:
    """Escribe el estado de foco (sobrescribe si ya existe).

    ``section`` es opcional; se incluye solo para reuniones inline.
    """
    data: dict = {"path": path, "type": type_, "day": day, "since": since}
    if section is not None:
        data["section"] = section
    focus_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def clear_focus(focus_file: Path = _FOCUS_FILE) -> None:
    """Vacía el foco. No-op si el archivo no existe."""
    if focus_file.exists():
        focus_file.write_text("", encoding="utf-8")


# ── Ejecutable ─────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Consulta el estado de foco")
    sub = parser.add_subparsers(dest="cmd")

    get_p = sub.add_parser("get", help="Devuelve el foco actual como JSON")
    get_p.add_argument("--focus-file", default=str(_FOCUS_FILE))

    args = parser.parse_args(argv)

    if args.cmd == "get":
        data = read_focus(Path(args.focus_file))
        print(json.dumps(data or {}, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
