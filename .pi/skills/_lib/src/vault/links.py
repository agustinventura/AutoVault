"""Inyección y mantenimiento de wikilinks en notas del vault.

Funciones puras sobre texto: no tocan el disco directamente.
"""

from __future__ import annotations

import re

from vault import markdown as md


def ensure_link_in_section(text: str, section: str, basename: str) -> str:
    """Añade ``[[basename]]`` a la sección si aún no está presente (idempotente).

    Lanza ``KeyError`` si la sección no existe.
    """
    wikilink = f"[[{basename}]]"
    body = md.get_section(text, section)
    if wikilink in body:
        return text
    return md.append_to_section(text, section, f"- {wikilink}")


# ── Agenda (W3/L2) ──────────────────────────────────────────────────────────

def inject_meeting_wikilink(text: str, meeting_name: str, note_basename: str) -> str:
    """Reemplaza la primera línea de la sección Agenda que contiene
    ``meeting_name`` (sin wikilink) por una versión con ``[[note_basename]]``.

    Lanza ``KeyError`` si no encuentra la reunión en la agenda.
    Es idempotente: si el wikilink ya está, no duplica.
    """
    wikilink = f"[[{note_basename}]]"
    section_body = md.get_section(text, "Agenda")

    # Si ya está inyectado no hacemos nada
    if wikilink in section_body:
        return text

    lines = section_body.splitlines()
    replaced = False
    new_lines = []
    for line in lines:
        if meeting_name in line and "[[" not in line:
            # Reemplaza la aparición del nombre por el wikilink
            new_lines.append(line.replace(meeting_name, wikilink, 1))
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        raise KeyError(f"Reunión {meeting_name!r} no encontrada en la Agenda")

    new_body = "\n".join(new_lines)
    return md.replace_section(text, "Agenda", new_body)


def insert_meeting_line(text: str, time: str, wikilink: str) -> str:
    """Inserta una nueva línea de reunión en la sección Agenda, ordenada
    cronológicamente por la hora de inicio (``HH:MM``).

    ``wikilink`` puede ser un wikilink ya formado, p. ej. ``[[20260625-Sync]]``.
    """
    new_line = f"- {time} {wikilink}"
    section_body = md.get_section(text, "Agenda")
    lines = section_body.splitlines()

    # Insertar en la posición correcta según la hora
    insert_pos = len(lines)
    for i, line in enumerate(lines):
        m = re.match(r"[-*]\s*(\d{2}:\d{2})", line)
        if m and m.group(1) > time:
            insert_pos = i
            break

    lines.insert(insert_pos, new_line)
    new_body = "\n".join(lines)
    return md.replace_section(text, "Agenda", new_body)


# ── Trabajado hoy ────────────────────────────────────────────────────────────

def ensure_worked_today(text: str, basename: str, time: str) -> str:
    """Añade una entrada ``- HH:MM [[basename]]`` a la sección *Trabajado hoy*
    si la entidad no está ya listada (idempotente: conserva la hora del primer
    foco, no duplica ni sobreescribe).
    """
    wikilink = f"[[{basename}]]"
    section_body = md.get_section(text, "Trabajado hoy")
    if wikilink in section_body:
        return text
    return md.append_to_section(text, "Trabajado hoy", f"- {time} {wikilink}")
