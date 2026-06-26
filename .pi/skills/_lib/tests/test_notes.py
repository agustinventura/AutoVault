"""Tests de vault.notes — append idempotente a sección Notas con ancla [[día]]."""

import subprocess
import sys
from pathlib import Path

from vault import notes


TASK_DOC = """\
---
type: task
status: en-curso
---
# Buscar usos

## Description
Desc.

## Notas

## Day close out
"""


class TestAppendNote:
    def test_inserts_day_anchor_if_absent(self):
        out = notes.append_note(TASK_DOC, day="20260625", text="- 10:00 primer apunte")
        assert "[[20260625]]" in out

    def test_anchor_only_inserted_once(self):
        once = notes.append_note(TASK_DOC, day="20260625", text="- 10:00 A")
        twice = notes.append_note(once, day="20260625", text="- 10:10 B")
        assert twice.count("[[20260625]]") == 1

    def test_bullet_appended_after_anchor(self):
        out = notes.append_note(TASK_DOC, day="20260625", text="- 10:00 hola")
        notas = _get_notas(out)
        lines = [l for l in notas.splitlines() if l.strip()]
        idx_anchor = next(i for i, l in enumerate(lines) if "[[20260625]]" in l)
        idx_bullet = next(i for i, l in enumerate(lines) if "hola" in l)
        assert idx_bullet > idx_anchor

    def test_multiple_bullets_same_day(self):
        out = notes.append_note(TASK_DOC, day="20260625", text="- 10:00 A")
        out = notes.append_note(out, day="20260625", text="- 10:10 B")
        notas = _get_notas(out)
        assert "A" in notas
        assert "B" in notas

    def test_different_days_get_separate_anchors(self):
        out = notes.append_note(TASK_DOC, day="20260625", text="- 10:00 A")
        out = notes.append_note(out, day="20260626", text="- 09:00 B")
        assert "[[20260625]]" in out
        assert "[[20260626]]" in out

    def test_does_not_leak_into_next_section(self):
        out = notes.append_note(TASK_DOC, day="20260625", text="- 10:00 X")
        close_out = _get_section(out, "Day close out")
        assert "X" not in close_out

    def test_target_section_name_override(self):
        doc = TASK_DOC.replace("## Notas", "## Notes")
        out = notes.append_note(doc, day="20260625", text="- 10:00 Y", section="Notes")
        assert "Y" in _get_section(out, "Notes")


class TestExecutableAppend:
    def test_appends_to_file(self, tmp_path):
        note_file = tmp_path / "T.md"
        note_file.write_text(TASK_DOC, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable, "-m", "vault.notes", "append",
                "--file", str(note_file),
                "--day", "20260625",
                "--text", "- 10:00 test",
            ],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        content = note_file.read_text(encoding="utf-8")
        assert "[[20260625]]" in content
        assert "- 10:00 test" in content


def _get_notas(text: str) -> str:
    from vault import markdown as md
    return md.get_section(text, "Notas")


def _get_section(text: str, name: str) -> str:
    from vault import markdown as md
    return md.get_section(text, name)
