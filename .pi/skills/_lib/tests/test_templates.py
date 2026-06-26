"""Tests de vault.templates — copia de plantilla y sustitución de {{token}}."""

from pathlib import Path

import pytest

from vault import templates


class TestRender:
    def test_substitutes_single_token(self):
        assert templates.render("Hola {{nombre}}", {"nombre": "Mango"}) == "Hola Mango"

    def test_substitutes_multiple_tokens(self):
        out = templates.render("{{a}} y {{b}}", {"a": "uno", "b": "dos"})
        assert out == "uno y dos"

    def test_missing_token_raises(self):
        with pytest.raises(KeyError):
            templates.render("{{falta}}", {})

    def test_does_not_touch_non_token_braces(self):
        # Dataview inline usa {field} (una llave), no debe verse afectado.
        src = "field: {value} y {{token}}"
        out = templates.render(src, {"token": "ok"})
        assert out == "field: {value} y ok"

    def test_token_may_appear_multiple_times(self):
        out = templates.render("{{x}}-{{x}}", {"x": "hi"})
        assert out == "hi-hi"


class TestApplyTemplate:
    def test_reads_template_and_renders(self, tmp_path):
        tpl = tmp_path / "Templates" / "task.md"
        tpl.parent.mkdir()
        tpl.write_text("# {{title}}\n\n## Notas\n", encoding="utf-8")

        out = templates.apply_template(tpl, {"title": "Mi tarea"})
        assert "# Mi tarea" in out
        assert "## Notas" in out

    def test_raises_if_template_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            templates.apply_template(tmp_path / "noexiste.md", {})


class TestCopyTemplate:
    def test_creates_destination_file(self, tmp_path):
        tpl = tmp_path / "Templates" / "task.md"
        tpl.parent.mkdir()
        tpl.write_text("# {{title}}\n", encoding="utf-8")

        dest = tmp_path / "Mango/Tickets/Tasks/T.md"
        templates.copy_template(tpl, dest, {"title": "Tarea test"})

        assert dest.exists()
        assert "# Tarea test" in dest.read_text(encoding="utf-8")

    def test_creates_intermediate_directories(self, tmp_path):
        tpl = tmp_path / "Templates" / "task.md"
        tpl.parent.mkdir()
        tpl.write_text("# {{title}}\n", encoding="utf-8")

        dest = tmp_path / "deep" / "nested" / "dir" / "note.md"
        templates.copy_template(tpl, dest, {"title": "x"})
        assert dest.exists()

    def test_does_not_overwrite_by_default(self, tmp_path):
        tpl = tmp_path / "Templates" / "task.md"
        tpl.parent.mkdir()
        tpl.write_text("# {{title}}\n", encoding="utf-8")
        dest = tmp_path / "note.md"
        dest.write_text("original", encoding="utf-8")

        with pytest.raises(FileExistsError):
            templates.copy_template(tpl, dest, {"title": "x"})

    def test_overwrite_flag_replaces_file(self, tmp_path):
        tpl = tmp_path / "Templates" / "task.md"
        tpl.parent.mkdir()
        tpl.write_text("# {{title}}\n", encoding="utf-8")
        dest = tmp_path / "note.md"
        dest.write_text("original", encoding="utf-8")

        templates.copy_template(tpl, dest, {"title": "nuevo"}, overwrite=True)
        assert "# nuevo" in dest.read_text(encoding="utf-8")
