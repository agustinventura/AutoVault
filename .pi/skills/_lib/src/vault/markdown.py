"""Lectura y escritura de Markdown: frontmatter YAML y secciones por encabezado.

Funciones puras sobre cadenas. El frontmatter se delimita con líneas '---'. Las
secciones se identifican por su encabezado ATX (p. ej. '## Notas'); el cuerpo de
una sección llega hasta el siguiente encabezado de igual o menor profundidad
(menos '#') o el fin del documento.
"""

from __future__ import annotations

import re

import yaml

_FENCE = "---"
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


# --- Frontmatter -----------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict, str]:
    """Separa (frontmatter, cuerpo). Sin frontmatter devuelve ({}, texto)."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != _FENCE:
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == _FENCE:
            raw = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            data = yaml.safe_load(raw) or {}
            return data, body
    # Fence de apertura sin cierre: se trata como cuerpo.
    return {}, text


def dump_document(frontmatter: dict, body: str) -> str:
    """Serializa frontmatter + cuerpo en un documento Markdown."""
    fm = yaml.safe_dump(
        frontmatter,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=None,
    ).rstrip("\n")
    if not body.startswith("\n"):
        body = "\n" + body if body else "\n"
    return f"{_FENCE}\n{fm}\n{_FENCE}{body}"


def get_field(text: str, key: str, default=None):
    fm, _ = split_frontmatter(text)
    return fm.get(key, default)


def set_field(text: str, key: str, value) -> str:
    fm, body = split_frontmatter(text)
    fm[key] = value
    return dump_document(fm, body)


# --- Secciones -------------------------------------------------------------

def _find_section_bounds(body_lines: list[str], name: str) -> tuple[int, int, int]:
    """Devuelve (idx_heading, body_start, body_end) de la sección ``name``.

    ``body_start`` es la primera línea tras el encabezado; ``body_end`` es el
    índice (exclusivo) donde acaba el cuerpo de la sección. Lanza ``KeyError``
    si no existe.
    """
    heading_idx = -1
    depth = 0
    for i, line in enumerate(body_lines):
        m = _HEADING_RE.match(line)
        if m and m.group(2) == name:
            heading_idx = i
            depth = len(m.group(1))
            break
    if heading_idx == -1:
        raise KeyError(f"Sección no encontrada: {name!r}")

    end = len(body_lines)
    for j in range(heading_idx + 1, len(body_lines)):
        m = _HEADING_RE.match(body_lines[j])
        if m and len(m.group(1)) <= depth:
            end = j
            break
    return heading_idx, heading_idx + 1, end


def has_section(text: str, name: str) -> bool:
    _, body = split_frontmatter(text)
    try:
        _find_section_bounds(body.splitlines(), name)
        return True
    except KeyError:
        return False


def get_section(text: str, name: str) -> str:
    """Cuerpo de la sección ``name`` (sin el encabezado). ``KeyError`` si falta."""
    _, body = split_frontmatter(text)
    lines = body.splitlines()
    _, start, end = _find_section_bounds(lines, name)
    return "\n".join(lines[start:end])


def _rebuild(text: str, lines: list[str]) -> str:
    fm, body = split_frontmatter(text)
    new_body = "\n".join(lines)
    if body.endswith("\n") and not new_body.endswith("\n"):
        new_body += "\n"
    if fm:
        return dump_document(fm, new_body)
    return new_body


def append_to_section(text: str, name: str, content: str) -> str:
    """Añade ``content`` al final del cuerpo de la sección ``name``.

    Inserta tras la última línea no vacía del cuerpo de la sección, de modo que
    no se filtra a la sección siguiente. ``KeyError`` si la sección no existe.
    """
    _, body = split_frontmatter(text)
    lines = body.splitlines()
    _, start, end = _find_section_bounds(lines, name)

    insert_at = end
    while insert_at > start and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    lines[insert_at:insert_at] = content.splitlines() or [content]
    return _rebuild(text, lines)


def replace_section(text: str, name: str, content: str) -> str:
    """Reemplaza por completo el cuerpo de la sección ``name`` por ``content``."""
    _, body = split_frontmatter(text)
    lines = body.splitlines()
    _, start, end = _find_section_bounds(lines, name)
    replacement = ["", *content.splitlines(), ""]
    lines[start:end] = replacement
    return _rebuild(text, lines)
