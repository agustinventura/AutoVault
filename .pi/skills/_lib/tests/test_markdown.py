"""Tests de vault.markdown — frontmatter YAML y secciones por encabezado.

Funciones puras sobre cadenas (no tocan disco). El frontmatter se delimita con
'---' al inicio del documento. Las secciones se identifican por su encabezado
ATX ('## Nombre').
"""

import pytest

from vault import markdown as md


SAMPLE = """\
---
type: task
status: pendiente
tags: [Mango, Kondo]
---
# Título

## Description
Una descripción.

## Notas

## Otra
fin
"""


class TestSplitFrontmatter:
    def test_parses_frontmatter_and_body(self):
        fm, body = md.split_frontmatter(SAMPLE)
        assert fm["type"] == "task"
        assert fm["status"] == "pendiente"
        assert fm["tags"] == ["Mango", "Kondo"]
        assert body.startswith("# Título")

    def test_no_frontmatter_returns_empty_dict(self):
        fm, body = md.split_frontmatter("# Solo cuerpo\n")
        assert fm == {}
        assert body == "# Solo cuerpo\n"


class TestDumpDocument:
    def test_roundtrip_preserves_fields(self):
        fm, body = md.split_frontmatter(SAMPLE)
        out = md.dump_document(fm, body)
        fm2, body2 = md.split_frontmatter(out)
        assert fm2 == fm
        assert body2.strip() == body.strip()

    def test_dump_starts_with_frontmatter_fence(self):
        out = md.dump_document({"type": "org"}, "# Mango\n")
        assert out.startswith("---\n")
        assert "type: org" in out


class TestFrontmatterField:
    def test_get_field(self):
        assert md.get_field(SAMPLE, "status") == "pendiente"

    def test_get_missing_field_returns_default(self):
        assert md.get_field(SAMPLE, "missing", default="x") == "x"

    def test_set_field_updates_value(self):
        out = md.set_field(SAMPLE, "status", "en-curso")
        assert md.get_field(out, "status") == "en-curso"
        # body intact
        assert "## Description" in out

    def test_set_field_adds_new_field(self):
        out = md.set_field(SAMPLE, "done", "2026-06-26")
        assert md.get_field(out, "done") == "2026-06-26"


class TestSections:
    def test_get_section_body(self):
        assert md.get_section(SAMPLE, "Description").strip() == "Una descripción."

    def test_get_missing_section_raises(self):
        with pytest.raises(KeyError):
            md.get_section(SAMPLE, "NoExiste")

    def test_has_section(self):
        assert md.has_section(SAMPLE, "Notas") is True
        assert md.has_section(SAMPLE, "NoExiste") is False

    def test_append_to_section_adds_line_at_end_of_section(self):
        out = md.append_to_section(SAMPLE, "Notas", "- 10:00 hola")
        notas = md.get_section(out, "Notas")
        assert "- 10:00 hola" in notas
        # must not leak into the following section
        assert "- 10:00 hola" not in md.get_section(out, "Otra")

    def test_append_preserves_existing_content(self):
        out = md.append_to_section(SAMPLE, "Description", "- extra")
        desc = md.get_section(out, "Description")
        assert "Una descripción." in desc
        assert "- extra" in desc

    def test_append_to_last_section(self):
        out = md.append_to_section(SAMPLE, "Otra", "- cola")
        assert "- cola" in md.get_section(out, "Otra")

    def test_replace_section_body(self):
        out = md.replace_section(SAMPLE, "Description", "Nuevo texto.")
        assert md.get_section(out, "Description").strip() == "Nuevo texto."
        assert md.get_section(out, "Notas") is not None

    def test_append_to_missing_section_raises(self):
        with pytest.raises(KeyError):
            md.append_to_section(SAMPLE, "NoExiste", "x")
