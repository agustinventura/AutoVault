"""Construcción y validación de rutas del vault, y saneo de nombres de archivo.

Las rutas se devuelven como ``PurePosixPath`` relativas al directorio raíz del
vault (Obsidian usa '/'). Las funciones son puras: no tocan el disco. La
resolución contra una raíz concreta es responsabilidad de los orquestadores.
"""

from __future__ import annotations

from pathlib import PurePosixPath

# Caracteres ilegales en nombres de archivo (se preservan espacios y acentos).
_RESERVED = set('/\\:*?"<>|')

DAILY_ROOT = "Daily log"
PROJECTS_DIR = "Proyectos"
INITIATIVES_DIR = "Iniciativas"
TICKETS_DIR = "Tickets"
TASKS_DIR = "Tasks"
MEETINGS_DIR = "Meetings"


def sanitize_filename(name: str) -> str:
    """Sanea un nombre para usarlo como archivo.

    Reemplaza los caracteres reservados por '-' y recorta espacios externos.
    Preserva espacios internos y acentos (válidos en macOS y Obsidian).
    Lanza ``ValueError`` si el resultado queda vacío.
    """
    cleaned = "".join("-" if c in _RESERVED else c for c in name).strip()
    if not cleaned:
        raise ValueError(f"Nombre inválido tras sanear: {name!r}")
    return cleaned


def _year_month(day: str) -> tuple[str, str]:
    """Extrae (AAAA, MM) de un identificador de día ``YYYYMMDD``."""
    return day[0:4], day[4:6]


# --- Notas diarias y semanales ---------------------------------------------

def daily_note(day: str) -> PurePosixPath:
    year, month = _year_month(day)
    return PurePosixPath(DAILY_ROOT) / year / month / f"{day}.md"


def weekly_summary(day: str, week_label: str) -> PurePosixPath:
    year, month = _year_month(day)
    return PurePosixPath(DAILY_ROOT) / year / month / f"{week_label}.md"


# --- Organización ----------------------------------------------------------

def org_dir(org: str) -> PurePosixPath:
    return PurePosixPath(org)


def org_note(org: str) -> PurePosixPath:
    return PurePosixPath(org) / f"{org}.md"


# --- Proyecto --------------------------------------------------------------

def project_dir(org: str, project: str) -> PurePosixPath:
    return PurePosixPath(org) / PROJECTS_DIR / project


def project_note(org: str, project: str) -> PurePosixPath:
    return project_dir(org, project) / f"{project}.md"


# --- Ticket ----------------------------------------------------------------

def ticket_note(org: str, ticket_id: str) -> PurePosixPath:
    return PurePosixPath(org) / TICKETS_DIR / f"{ticket_id}.md"


def ticket_task_note(org: str, ticket_id: str, title: str) -> PurePosixPath:
    name = sanitize_filename(f"{ticket_id}_{title}")
    return PurePosixPath(org) / TICKETS_DIR / TASKS_DIR / f"{name}.md"


# --- Iniciativa ------------------------------------------------------------

def initiative_dir(org: str, project: str, initiative: str) -> PurePosixPath:
    return project_dir(org, project) / INITIATIVES_DIR / initiative


def initiative_note(org: str, project: str, initiative: str) -> PurePosixPath:
    return initiative_dir(org, project, initiative) / f"{initiative}.md"


def initiative_task_note(
    org: str, project: str, initiative: str, title: str
) -> PurePosixPath:
    name = sanitize_filename(title)
    return initiative_dir(org, project, initiative) / TASKS_DIR / f"{name}.md"


# --- Reunión ---------------------------------------------------------------

def meeting_note(org: str, day: str, name: str) -> PurePosixPath:
    year, month = _year_month(day)
    safe = sanitize_filename(f"{day}-{name}")
    return PurePosixPath(org) / MEETINGS_DIR / year / month / f"{safe}.md"


# --- Wikilinks y nombres ---------------------------------------------------

def note_basename(path: str | PurePosixPath) -> str:
    """Nombre de la nota sin extensión (basename del archivo)."""
    return PurePosixPath(path).stem


def wikilink(basename: str) -> str:
    """Wikilink de Obsidian a partir de un basename: ``[[basename]]``."""
    return f"[[{basename}]]"


def wikilink_for(path: str | PurePosixPath) -> str:
    """Wikilink de Obsidian a partir de una ruta de nota."""
    return wikilink(note_basename(path))
