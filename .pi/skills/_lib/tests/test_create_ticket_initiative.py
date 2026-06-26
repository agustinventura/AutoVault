"""Tests de integración de create_ticket.py y create_initiative.py."""

import json

from conftest import skill_script, run_script


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


def setup_mango_kondo(vault):
    run("create-org", vault, "--name", "Mango")
    run("create-project", vault, "--org", "Mango", "--name", "Kondo",
        "--description", "Gestión de listados")


# ── create-ticket ────────────────────────────────────────────────────────────

class TestCreateTicket:
    def test_creates_ticket_note(self, vault):
        setup_mango_kondo(vault)
        r = run("create-ticket", vault,
                "--org", "Mango", "--project", "Kondo",
                "--id", "ONLINE-173894",
                "--title", "Eliminar dependencia IMAGE_TRANSITION",
                "--target", "Eliminar la tabla",
                "--description", "Descripción original del ticket")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
        assert (vault / "Mango" / "Tickets" / "ONLINE-173894.md").exists()

    def test_frontmatter_fields(self, vault):
        setup_mango_kondo(vault)
        run("create-ticket", vault,
            "--org", "Mango", "--project", "Kondo",
            "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        from vault import markdown as md
        content = (vault / "Mango" / "Tickets" / "ONLINE-1.md").read_text(encoding="utf-8")
        assert md.get_field(content, "type") == "ticket"
        assert md.get_field(content, "id") == "ONLINE-1"
        assert md.get_field(content, "org") == "Mango"
        assert md.get_field(content, "project") == "Kondo"
        assert "ONLINE-1" in md.get_field(content, "tags")

    def test_adds_wikilink_to_project_enlaces(self, vault):
        setup_mango_kondo(vault)
        run("create-ticket", vault,
            "--org", "Mango", "--project", "Kondo",
            "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        from vault import markdown as md
        project_note = (vault / "Mango" / "Proyectos" / "Kondo" / "Kondo.md").read_text(encoding="utf-8")
        assert "[[ONLINE-1]]" in md.get_section(project_note, "Enlaces")

    def test_fails_if_project_missing(self, vault):
        run("create-org", vault, "--name", "Mango")
        r = run("create-ticket", vault,
                "--org", "Mango", "--project", "NoExiste",
                "--id", "T-1", "--title", "T", "--target", "X", "--description", "D")
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "PROJECT_NOT_FOUND"

    def test_idempotent(self, vault):
        setup_mango_kondo(vault)
        run("create-ticket", vault,
            "--org", "Mango", "--project", "Kondo",
            "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        r = run("create-ticket", vault,
                "--org", "Mango", "--project", "Kondo",
                "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True


# ── create-initiative ────────────────────────────────────────────────────────

def setup_capitole_charla(vault):
    run("create-org", vault, "--name", "Capitole")
    run("create-project", vault, "--org", "Capitole",
        "--name", "Charla Multiagentes", "--description", "Charla técnica")


class TestCreateInitiative:
    def test_creates_initiative_note(self, vault):
        setup_capitole_charla(vault)
        r = run("create-initiative", vault,
                "--org", "Capitole", "--project", "Charla Multiagentes",
                "--name", "Adaptar Presentación",
                "--description", "Adaptar para el nuevo público")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
        note = (vault / "Capitole" / "Proyectos" / "Charla Multiagentes"
                / "Iniciativas" / "Adaptar Presentación" / "Adaptar Presentación.md")
        assert note.exists()

    def test_frontmatter_fields(self, vault):
        setup_capitole_charla(vault)
        run("create-initiative", vault,
            "--org", "Capitole", "--project", "Charla Multiagentes",
            "--name", "Adaptar Presentación", "--description", "Desc")
        from vault import markdown as md
        note_path = (vault / "Capitole" / "Proyectos" / "Charla Multiagentes"
                     / "Iniciativas" / "Adaptar Presentación" / "Adaptar Presentación.md")
        content = note_path.read_text(encoding="utf-8")
        assert md.get_field(content, "type") == "initiative"
        assert md.get_field(content, "org") == "Capitole"
        assert "Adaptar Presentación" in md.get_field(content, "tags")

    def test_adds_wikilink_to_project_enlaces(self, vault):
        setup_capitole_charla(vault)
        run("create-initiative", vault,
            "--org", "Capitole", "--project", "Charla Multiagentes",
            "--name", "Adaptar Presentación", "--description", "Desc")
        from vault import markdown as md
        project_note = (vault / "Capitole" / "Proyectos" / "Charla Multiagentes"
                        / "Charla Multiagentes.md").read_text(encoding="utf-8")
        assert "[[Adaptar Presentación]]" in md.get_section(project_note, "Enlaces")

    def test_fails_if_project_missing(self, vault):
        run("create-org", vault, "--name", "Capitole")
        r = run("create-initiative", vault,
                "--org", "Capitole", "--project", "NoExiste",
                "--name", "X", "--description", "D")
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "PROJECT_NOT_FOUND"

    def test_idempotent(self, vault):
        setup_capitole_charla(vault)
        run("create-initiative", vault,
            "--org", "Capitole", "--project", "Charla Multiagentes",
            "--name", "Adaptar Presentación", "--description", "Desc")
        r = run("create-initiative", vault,
                "--org", "Capitole", "--project", "Charla Multiagentes",
                "--name", "Adaptar Presentación", "--description", "Desc")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
