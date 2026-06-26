"""Tests de vault.tasks — FSM, walk del filesystem, sincronización status↔tag.

Los tests de FSM y sincronización son puros (sin disco). El walk se testea con
tmp_path (integración mínima).
"""

from pathlib import Path

import pytest

from vault import tasks


# ── FSM ────────────────────────────────────────────────────────────────────

class TestValidTransitions:
    def test_pendiente_to_en_curso(self):
        assert tasks.can_transition("pendiente", "en-curso")

    def test_en_curso_to_pendiente(self):
        assert tasks.can_transition("en-curso", "pendiente")

    def test_en_curso_to_bloqueada(self):
        assert tasks.can_transition("en-curso", "bloqueada")

    def test_en_curso_to_terminada(self):
        assert tasks.can_transition("en-curso", "terminada")

    def test_bloqueada_to_en_curso(self):
        assert tasks.can_transition("bloqueada", "en-curso")

    def test_bloqueada_to_terminada(self):
        assert tasks.can_transition("bloqueada", "terminada")


class TestInvalidTransitions:
    def test_terminada_is_terminal(self):
        assert not tasks.can_transition("terminada", "en-curso")
        assert not tasks.can_transition("terminada", "pendiente")
        assert not tasks.can_transition("terminada", "bloqueada")

    def test_pendiente_cannot_jump_to_terminada_directly(self):
        assert not tasks.can_transition("pendiente", "terminada")

    def test_pendiente_cannot_go_bloqueada(self):
        assert not tasks.can_transition("pendiente", "bloqueada")

    def test_bloqueada_cannot_go_pendiente(self):
        assert not tasks.can_transition("bloqueada", "pendiente")

    def test_unknown_status_raises(self):
        with pytest.raises(ValueError):
            tasks.can_transition("fantasma", "en-curso")


class TestValidateTransition:
    def test_raises_on_invalid_transition(self):
        with pytest.raises(tasks.InvalidTransitionError):
            tasks.validate_transition("terminada", "pendiente")

    def test_ok_on_valid_transition(self):
        tasks.validate_transition("pendiente", "en-curso")  # must not raise


# ── Tag sincronizado ────────────────────────────────────────────────────────

TASK_DOC = """\
---
type: task
status: pendiente
tags:
- Mango
- Kondo
- ONLINE-173894
- tarea/pendiente
---
# Buscar usos

## Description
Desc.

## Notas
"""


class TestSyncStatusTag:
    def test_updates_status_field(self):
        out = tasks.set_status(TASK_DOC, "en-curso")
        from vault import markdown as md
        assert md.get_field(out, "status") == "en-curso"

    def test_updates_status_tag(self):
        out = tasks.set_status(TASK_DOC, "en-curso")
        from vault import markdown as md
        assert "tarea/en-curso" in md.get_field(out, "tags")

    def test_removes_old_status_tag(self):
        out = tasks.set_status(TASK_DOC, "en-curso")
        from vault import markdown as md
        assert "tarea/pendiente" not in md.get_field(out, "tags")

    def test_sets_done_field_on_terminada(self):
        out = tasks.set_status(TASK_DOC, "en-curso")
        out = tasks.set_status(out, "terminada", done_date="2026-06-26")
        from vault import markdown as md
        assert md.get_field(out, "done") == "2026-06-26"

    def test_raises_on_invalid_transition(self):
        with pytest.raises(tasks.InvalidTransitionError):
            tasks.set_status(TASK_DOC, "terminada")  # pendiente → terminada inválido


# ── Walk del filesystem ─────────────────────────────────────────────────────

def _make_task(path: Path, status: str, org: str = "Mango") -> None:
    """Crea una nota de tarea mínima con frontmatter en tmp_path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntype: task\nstatus: {status}\norg: {org}\ntags: [tarea/{status}]\n---\n# T\n",
        encoding="utf-8",
    )


def _make_non_task(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntype: daily\n---\n# D\n", encoding="utf-8")


class TestWalkTasks:
    def test_finds_tasks_by_status(self, tmp_path):
        _make_task(tmp_path / "Mango/Tickets/Tasks/T1.md", "pendiente")
        _make_task(tmp_path / "Mango/Tickets/Tasks/T2.md", "en-curso")
        _make_task(tmp_path / "Mango/Tickets/Tasks/T3.md", "terminada")
        _make_non_task(tmp_path / "Daily log/2026/06/20260625.md")

        found = tasks.find_tasks(tmp_path, statuses={"pendiente", "en-curso"})
        names = {p.name for p in found}
        assert names == {"T1.md", "T2.md"}

    def test_ignores_non_task_notes(self, tmp_path):
        _make_non_task(tmp_path / "Daily log/2026/06/20260625.md")
        found = tasks.find_tasks(tmp_path, statuses={"pendiente"})
        assert found == []

    def test_finds_tasks_under_initiatives(self, tmp_path):
        _make_task(
            tmp_path / "Capitole/Proyectos/P/Iniciativas/I/Tasks/T.md",
            "bloqueada",
            org="Capitole",
        )
        found = tasks.find_tasks(tmp_path, statuses={"bloqueada"})
        assert len(found) == 1

    def test_returns_paths_relative_to_root(self, tmp_path):
        _make_task(tmp_path / "Mango/Tickets/Tasks/T1.md", "pendiente")
        found = tasks.find_tasks(tmp_path, statuses={"pendiente"})
        assert all(not p.is_absolute() for p in found)
