"""Máquina de estados de tareas, walk del vault y sincronización status↔tag.

Estados: pendiente | en-curso | bloqueada | terminada (terminal).

Transiciones válidas:
  pendiente  → en-curso
  en-curso   → pendiente | bloqueada | terminada
  bloqueada  → en-curso  | terminada
  terminada  → (ninguna, estado terminal)
"""

from __future__ import annotations

from pathlib import Path

from vault import markdown as md

# ── FSM ────────────────────────────────────────────────────────────────────

VALID_STATUSES = frozenset({"pendiente", "en-curso", "bloqueada", "terminada"})

_TRANSITIONS: dict[str, frozenset[str]] = {
    "pendiente": frozenset({"en-curso"}),
    "en-curso":  frozenset({"pendiente", "bloqueada", "terminada"}),
    "bloqueada": frozenset({"en-curso", "terminada"}),
    "terminada": frozenset(),
}

_TAG_PREFIX = "tarea/"


class InvalidTransitionError(Exception):
    """Transición de estado no permitida por la FSM."""


def can_transition(from_status: str, to_status: str) -> bool:
    """``True`` si la transición está permitida. ``ValueError`` si el estado origen es desconocido."""
    if from_status not in _TRANSITIONS:
        raise ValueError(f"Estado desconocido: {from_status!r}")
    return to_status in _TRANSITIONS[from_status]


def validate_transition(from_status: str, to_status: str) -> None:
    """Lanza ``InvalidTransitionError`` si la transición no está permitida."""
    if not can_transition(from_status, to_status):
        raise InvalidTransitionError(
            f"Transición inválida: {from_status!r} → {to_status!r}"
        )


# ── Sincronización status ↔ tag ─────────────────────────────────────────────

def set_status(text: str, new_status: str, done_date: str | None = None) -> str:
    """Actualiza ``status`` y el tag ``tarea/…`` en el frontmatter del documento.

    Valida que la transición desde el estado actual sea legal (``InvalidTransitionError``).
    Si ``new_status`` es ``"terminada"`` y se pasa ``done_date``, establece el campo ``done``.
    """
    current = md.get_field(text, "status")
    validate_transition(current, new_status)

    # Actualizar campo status
    out = md.set_field(text, "status", new_status)

    # Sincronizar tag: quitar el tag de estado anterior, añadir el nuevo
    tags: list = md.get_field(out, "tags") or []
    tags = [t for t in tags if not t.startswith(_TAG_PREFIX)]
    tags.append(f"{_TAG_PREFIX}{new_status}")
    out = md.set_field(out, "tags", tags)

    # Campo done al terminar
    if new_status == "terminada" and done_date:
        out = md.set_field(out, "done", done_date)

    return out


# ── Walk del filesystem ─────────────────────────────────────────────────────

def find_tasks(vault_root: Path, statuses: set[str]) -> list[Path]:
    """Devuelve rutas relativas a ``vault_root`` de notas de tipo ``task``
    cuyo ``status`` pertenece a ``statuses``.

    Ignora dotdirs y ``node_modules``. No requiere Obsidian corriendo.
    """
    results: list[Path] = []
    for path in vault_root.rglob("*.md"):
        # Ignorar dotdirs, node_modules y la carpeta de plantillas
        parts = path.parts
        if any(part.startswith(".") for part in parts):
            continue
        if "node_modules" in parts:
            continue
        if "Templates" in parts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            note_type = md.get_field(content, "type")
            status = md.get_field(content, "status")
        except Exception:
            continue
        if note_type != "task":
            continue
        if status in statuses:
            results.append(path.relative_to(vault_root))
    return results
