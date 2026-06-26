"""Tests de integración de create_task.py."""

import json

from conftest import skill_script, run_script


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


def setup_mango_kondo_ticket(vault):
    run("create-org", vault, "--name", "Mango")
    run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
    run("create-ticket", vault,
        "--org", "Mango", "--project", "Kondo",
        "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")


def setup_capitole_initiative(vault):
    run("create-org", vault, "--name", "Capitole")
    run("create-project", vault, "--org", "Capitole",
        "--name", "Charla Multiagentes", "--description", "x")
    run("create-initiative", vault,
        "--org", "Capitole", "--project", "Charla Multiagentes",
        "--name", "Adaptar Presentación", "--description", "x")


class TestCreateTaskFromTicket:
    def test_creates_task_note(self, vault):
        setup_mango_kondo_ticket(vault)
        r = run("create-task", vault,
                "--org", "Mango", "--ticket", "ONLINE-1",
                "--title", "Buscar usos de las tablas",
                "--description", "Buscar todos los usos")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
        note = vault / "Mango" / "Tickets" / "Tasks" / "ONLINE-1_Buscar usos de las tablas.md"
        assert note.exists()

    def test_frontmatter_status_pendiente(self, vault):
        setup_mango_kondo_ticket(vault)
        run("create-task", vault,
            "--org", "Mango", "--ticket", "ONLINE-1",
            "--title", "T1", "--description", "D")
        from vault import markdown as md
        note = vault / "Mango" / "Tickets" / "Tasks" / "ONLINE-1_T1.md"
        content = note.read_text(encoding="utf-8")
        assert md.get_field(content, "status") == "pendiente"
        assert md.get_field(content, "type") == "task"
        assert "tarea/pendiente" in md.get_field(content, "tags")

    def test_adds_wikilink_to_ticket_tareas(self, vault):
        setup_mango_kondo_ticket(vault)
        run("create-task", vault,
            "--org", "Mango", "--ticket", "ONLINE-1",
            "--title", "Buscar usos", "--description", "D")
        from vault import markdown as md
        ticket = (vault / "Mango" / "Tickets" / "ONLINE-1.md").read_text(encoding="utf-8")
        assert "[[ONLINE-1_Buscar usos]]" in md.get_section(ticket, "Tareas")

    def test_fails_if_ticket_missing(self, vault):
        run("create-org", vault, "--name", "Mango")
        r = run("create-task", vault,
                "--org", "Mango", "--ticket", "NOEXISTE",
                "--title", "T", "--description", "D")
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "PARENT_NOT_FOUND"

    def test_idempotent(self, vault):
        setup_mango_kondo_ticket(vault)
        run("create-task", vault,
            "--org", "Mango", "--ticket", "ONLINE-1",
            "--title", "T1", "--description", "D")
        r = run("create-task", vault,
                "--org", "Mango", "--ticket", "ONLINE-1",
                "--title", "T1", "--description", "D")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True


class TestCreateTaskFromInitiative:
    def test_creates_task_note_without_id_prefix(self, vault):
        setup_capitole_initiative(vault)
        r = run("create-task", vault,
                "--org", "Capitole",
                "--initiative", "Adaptar Presentación",
                "--project", "Charla Multiagentes",
                "--title", "Acortar presentación",
                "--description", "Reducir a 20 slides")
        assert r.returncode == 0
        note = (vault / "Capitole" / "Proyectos" / "Charla Multiagentes"
                / "Iniciativas" / "Adaptar Presentación" / "Tasks"
                / "Acortar presentación.md")
        assert note.exists()

    def test_adds_wikilink_to_initiative_tareas(self, vault):
        setup_capitole_initiative(vault)
        run("create-task", vault,
            "--org", "Capitole",
            "--initiative", "Adaptar Presentación",
            "--project", "Charla Multiagentes",
            "--title", "Acortar presentación",
            "--description", "D")
        from vault import markdown as md
        ini_note = (vault / "Capitole" / "Proyectos" / "Charla Multiagentes"
                    / "Iniciativas" / "Adaptar Presentación"
                    / "Adaptar Presentación.md").read_text(encoding="utf-8")
        assert "[[Acortar presentación]]" in md.get_section(ini_note, "Tareas")
