"""Append idempotente de notas con ancla [[YYYYMMDD]] en una sección Markdown.

Ejecutable:
    python -m vault.notes append --file PATH --day YYYYMMDD --text "- HH:MM …"
"""

from __future__ import annotations

from pathlib import Path

from vault import markdown as md
from vault.markdown import _find_section_bounds

_DEFAULT_SECTION = "Notas"
_ANCHOR_TEMPLATE = "[[{day}]]"


def append_note(
    document: str,
    *,
    day: str,
    text: str,
    section: str = _DEFAULT_SECTION,
) -> str:
    """Añade ``text`` a ``section`` bajo la ancla ``[[day]]``.

    - Si la ancla no existe en la sección, la inserta junto con el bullet.
    - No duplica la ancla (idempotente).
    - Bullets nuevos se añaden tras los ya existentes del mismo día.
    """
    anchor = _ANCHOR_TEMPLATE.format(day=day)
    section_body = md.get_section(document, section)

    if anchor not in section_body:
        entry = f"{anchor}\n{text}"
        return md.append_to_section(document, section, entry)
    else:
        return _append_after_anchor(document, anchor, text, section)


def _append_after_anchor(document: str, anchor: str, new_line: str, section: str) -> str:
    """Inserta ``new_line`` dentro del bloque del día, antes del siguiente ancla."""
    _, body = md.split_frontmatter(document)
    lines = body.splitlines()

    _, sec_start, sec_end = _find_section_bounds(lines, section)

    # Localizar la ancla del día
    anchor_idx = None
    for i in range(sec_start, sec_end):
        if anchor in lines[i]:
            anchor_idx = i
            break

    # El bloque del día llega hasta la siguiente ancla [[…]] o fin de la sección
    block_end = sec_end
    for j in range(anchor_idx + 1, sec_end):
        stripped = lines[j].strip()
        if stripped.startswith("[[") and stripped.endswith("]]"):
            block_end = j
            break

    # Insertar antes de las líneas vacías al final del bloque
    insert_at = block_end
    while insert_at > anchor_idx + 1 and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    lines.insert(insert_at, new_line)

    new_body = "\n".join(lines)
    fm, _ = md.split_frontmatter(document)
    if fm:
        prefix = "\n" if not new_body.startswith("\n") else ""
        return md.dump_document(fm, prefix + new_body)
    return new_body


# ── Ejecutable ─────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Append de notas al vault")
    sub = parser.add_subparsers(dest="cmd")

    ap = sub.add_parser("append")
    ap.add_argument("--file", required=True)
    ap.add_argument("--day", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--section", default=_DEFAULT_SECTION)

    args = parser.parse_args(argv)

    if args.cmd == "append":
        path = Path(args.file)
        content = path.read_text(encoding="utf-8")
        out = append_note(content, day=args.day, text=args.text, section=args.section)
        path.write_text(out, encoding="utf-8")
        print(json.dumps({"ok": True}))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
