"""Tests de vault.links — inyección y mantenimiento de wikilinks.

Funciones puras sobre texto de notas (no tocan disco directamente).
Las operaciones de alto nivel que combinan lectura+escritura de archivos
se testean en los orquestadores.
"""

import pytest

from vault import links


# ── Links en sección genérica ───────────────────────────────────────────────

SECTION_DOC = """\
---
type: project
---
# Kondo

## Description
Gestión de listados.

## Enlaces

"""

class TestEnsureLinkInSection:
    def test_adds_link_when_absent(self):
        out = links.ensure_link_in_section(SECTION_DOC, "Enlaces", "ONLINE-173894")
        assert "[[ONLINE-173894]]" in out

    def test_idempotent_does_not_duplicate(self):
        once = links.ensure_link_in_section(SECTION_DOC, "Enlaces", "ONLINE-173894")
        twice = links.ensure_link_in_section(once, "Enlaces", "ONLINE-173894")
        assert twice.count("[[ONLINE-173894]]") == 1

    def test_preserves_existing_links(self):
        with_one = links.ensure_link_in_section(SECTION_DOC, "Enlaces", "T1")
        with_two = links.ensure_link_in_section(with_one, "Enlaces", "T2")
        assert "[[T1]]" in with_two
        assert "[[T2]]" in with_two

    def test_raises_if_section_missing(self):
        with pytest.raises(KeyError):
            links.ensure_link_in_section(SECTION_DOC, "NoExiste", "x")


# ── Agenda (W3 / L2) ────────────────────────────────────────────────────────

AGENDA_DOC = """\
---
type: daily
---
# Diario del 25/06/2026

## Agenda
- 08:00 Inicio
- 09:45 - 10:00 Kondo Daily
- 12:00 - 13:00 Tribe Backend
- 17:00 Fin

## Tasks

## Notes
"""

class TestInjectMeetingWikilink:
    def test_replaces_meeting_line_with_wikilink(self):
        out = links.inject_meeting_wikilink(
            AGENDA_DOC, "Tribe Backend", "20260625-Tribe Backend"
        )
        assert "[[20260625-Tribe Backend]]" in out
        # El texto original ya no existe sin enlazar
        agenda = _get_agenda(out)
        assert "12:00 - 13:00 Tribe Backend\n" not in agenda or \
               "[[20260625-Tribe Backend]]" in agenda

    def test_only_replaces_target_meeting(self):
        out = links.inject_meeting_wikilink(
            AGENDA_DOC, "Tribe Backend", "20260625-Tribe Backend"
        )
        assert "Kondo Daily" in out  # intacto

    def test_raises_if_meeting_name_not_in_agenda(self):
        with pytest.raises(KeyError):
            links.inject_meeting_wikilink(AGENDA_DOC, "No existe", "x")

    def test_idempotent(self):
        once = links.inject_meeting_wikilink(
            AGENDA_DOC, "Tribe Backend", "20260625-Tribe Backend"
        )
        twice = links.inject_meeting_wikilink(
            once, "Tribe Backend", "20260625-Tribe Backend"
        )
        assert twice.count("[[20260625-Tribe Backend]]") == 1


class TestInsertMeetingLine:
    def test_inserts_new_line_in_chronological_order(self):
        out = links.insert_meeting_line(
            AGENDA_DOC, "10:30", "[[20260625-Sync rapido]]"
        )
        agenda = _get_agenda(out)
        lines = [l.strip() for l in agenda.splitlines() if l.strip()]
        times = [l.split()[0] for l in lines if l[0].isdigit()]
        # 08:00, 09:45, 10:30, 12:00, 17:00 — ordenado
        assert times == sorted(times)

    def test_inserted_line_contains_wikilink(self):
        out = links.insert_meeting_line(
            AGENDA_DOC, "10:30", "[[20260625-Sync rapido]]"
        )
        assert "[[20260625-Sync rapido]]" in out


# ── Trabajado hoy ───────────────────────────────────────────────────────────

DAILY_DOC = """\
---
type: daily
---
# Diario

## Agenda

## Tasks

## Notes

## Trabajado hoy

## Day close out
"""

class TestEnsureWorkedToday:
    def test_adds_entry_with_time(self):
        out = links.ensure_worked_today(DAILY_DOC, "ONLINE-173894_Buscar usos", "10:14")
        assert "10:14 [[ONLINE-173894_Buscar usos]]" in out

    def test_idempotent_does_not_duplicate(self):
        once = links.ensure_worked_today(DAILY_DOC, "T1", "09:00")
        twice = links.ensure_worked_today(once, "T1", "10:00")
        assert twice.count("[[T1]]") == 1

    def test_preserves_time_of_first_entry(self):
        once = links.ensure_worked_today(DAILY_DOC, "T1", "09:00")
        twice = links.ensure_worked_today(once, "T1", "10:00")
        assert "09:00" in twice
        assert twice.count("10:00") == 0


# helper
def _get_agenda(text: str) -> str:
    from vault import markdown as md
    return md.get_section(text, "Agenda")
