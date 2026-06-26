"""Tests de vault.paths — construcción y validación de rutas, saneo de nombres.

Las rutas se devuelven como Path relativos al directorio raíz del vault, en
formato POSIX (Obsidian usa '/'). Las funciones son puras (no tocan disco).
"""

from pathlib import PurePosixPath

import pytest

from vault import paths


class TestSanitizeFilename:
    def test_keeps_spaces_and_accents(self):
        assert paths.sanitize_filename("Adaptar Presentación") == "Adaptar Presentación"

    def test_replaces_illegal_characters_with_dash(self):
        assert paths.sanitize_filename("a/b:c*d?") == "a-b-c-d-"

    def test_replaces_all_reserved_set(self):
        assert paths.sanitize_filename(r'x\y:z*q?w"e<r>t|u') == "x-y-z-q-w-e-r-t-u"

    def test_strips_surrounding_whitespace(self):
        assert paths.sanitize_filename("  hola  ") == "hola"

    def test_rejects_empty_after_strip(self):
        with pytest.raises(ValueError):
            paths.sanitize_filename("   ")


class TestDailyPaths:
    def test_daily_note(self):
        assert paths.daily_note("20260625") == PurePosixPath(
            "Daily log/2026/06/20260625.md"
        )

    def test_weekly_summary(self):
        assert paths.weekly_summary("20260625", "W-26") == PurePosixPath(
            "Daily log/2026/06/W-26.md"
        )


class TestOrgPaths:
    def test_org_note(self):
        assert paths.org_note("Mango") == PurePosixPath("Mango/Mango.md")

    def test_org_dir(self):
        assert paths.org_dir("Mango") == PurePosixPath("Mango")


class TestProjectPaths:
    def test_project_note(self):
        assert paths.project_note("Mango", "Kondo") == PurePosixPath(
            "Mango/Proyectos/Kondo/Kondo.md"
        )

    def test_project_dir(self):
        assert paths.project_dir("Mango", "Kondo") == PurePosixPath(
            "Mango/Proyectos/Kondo"
        )


class TestTicketPaths:
    def test_ticket_note(self):
        assert paths.ticket_note("Mango", "ONLINE-173894") == PurePosixPath(
            "Mango/Tickets/ONLINE-173894.md"
        )

    def test_ticket_task_note_uses_id_prefix(self):
        assert paths.ticket_task_note(
            "Mango", "ONLINE-173894", "Buscar usos de las tablas"
        ) == PurePosixPath(
            "Mango/Tickets/Tasks/ONLINE-173894_Buscar usos de las tablas.md"
        )

    def test_ticket_task_note_sanitizes_title(self):
        assert paths.ticket_task_note(
            "Mango", "ONLINE-1", "a/b"
        ) == PurePosixPath("Mango/Tickets/Tasks/ONLINE-1_a-b.md")


class TestInitiativePaths:
    def test_initiative_note(self):
        assert paths.initiative_note(
            "Capitole", "Charla Multiagentes", "Adaptar Presentación"
        ) == PurePosixPath(
            "Capitole/Proyectos/Charla Multiagentes/Iniciativas/"
            "Adaptar Presentación/Adaptar Presentación.md"
        )

    def test_initiative_task_note_no_id_prefix(self):
        assert paths.initiative_task_note(
            "Capitole", "Charla Multiagentes", "Adaptar Presentación", "Acortar presentación"
        ) == PurePosixPath(
            "Capitole/Proyectos/Charla Multiagentes/Iniciativas/"
            "Adaptar Presentación/Tasks/Acortar presentación.md"
        )


class TestMeetingPaths:
    def test_meeting_note(self):
        assert paths.meeting_note("Mango", "20260625", "Tribe Backend") == PurePosixPath(
            "Mango/Meetings/2026/06/20260625-Tribe Backend.md"
        )

    def test_meeting_note_sanitizes_name(self):
        assert paths.meeting_note("Mango", "20260625", "Sync a/b") == PurePosixPath(
            "Mango/Meetings/2026/06/20260625-Sync a-b.md"
        )


class TestNoteBasename:
    def test_returns_filename_without_extension(self):
        p = PurePosixPath("Mango/Tickets/ONLINE-173894.md")
        assert paths.note_basename(p) == "ONLINE-173894"

    def test_works_with_string(self):
        assert paths.note_basename("Daily log/2026/06/20260625.md") == "20260625"


class TestWikilink:
    def test_builds_wikilink_from_basename(self):
        assert paths.wikilink("20260625") == "[[20260625]]"

    def test_builds_wikilink_from_path(self):
        p = PurePosixPath("Mango/Tickets/ONLINE-173894.md")
        assert paths.wikilink_for(p) == "[[ONLINE-173894]]"
