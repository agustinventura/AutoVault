"""Tests de integración de start_day.py."""

import json
from datetime import date

from conftest import skill_script, run_script
from vault import markdown as md


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


AGENDA_JSON = json.dumps({
    "start": "08:00",
    "end": "17:00",
    "breaks": [{"name": "Desayuno", "start": "10:00", "end": "10:30"}],
    "meetings": [{"name": "Kondo Daily", "start": "09:45", "end": "10:00"}],
})

PRIORITIES_JSON = json.dumps(["ONLINE-1_T1", "ONLINE-1_T2"])


def setup_tasks(vault):
    """Crea org, proyecto, ticket y dos tareas pendientes."""
    run("create-org", vault, "--name", "Mango")
    run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
    run("create-ticket", vault,
        "--org", "Mango", "--project", "Kondo",
        "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
    run("create-task", vault,
        "--org", "Mango", "--ticket", "ONLINE-1",
        "--title", "T1", "--description", "D")
    run("create-task", vault,
        "--org", "Mango", "--ticket", "ONLINE-1",
        "--title", "T2", "--description", "D")


class TestStartDay:
    def test_creates_daily_note(self, vault):
        today = date.today().strftime("%Y%m%d")
        r = run("start-day", vault,
                "--day", today,
                "--agenda", AGENDA_JSON,
                "--priorities", PRIORITIES_JSON)
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
        year, month = today[:4], today[4:6]
        note = vault / "Daily log" / year / month / f"{today}.md"
        assert note.exists()

    def test_daily_frontmatter(self, vault):
        today = date.today().strftime("%Y%m%d")
        run("start-day", vault,
            "--day", today,
            "--agenda", AGENDA_JSON,
            "--priorities", PRIORITIES_JSON)
        year, month = today[:4], today[4:6]
        content = (vault / "Daily log" / year / month / f"{today}.md").read_text(encoding="utf-8")
        assert md.get_field(content, "type") == "daily"
        assert str(md.get_field(content, "date")) == f"{today[:4]}-{today[4:6]}-{today[6:]}"

    def test_agenda_section_contains_meetings(self, vault):
        today = date.today().strftime("%Y%m%d")
        run("start-day", vault,
            "--day", today,
            "--agenda", AGENDA_JSON,
            "--priorities", PRIORITIES_JSON)
        year, month = today[:4], today[4:6]
        content = (vault / "Daily log" / year / month / f"{today}.md").read_text(encoding="utf-8")
        agenda = md.get_section(content, "Agenda")
        assert "Kondo Daily" in agenda
        assert "Desayuno" in agenda
        assert "08:00" in agenda
        assert "17:00" in agenda

    def test_tasks_section_contains_pending_tasks(self, vault):
        setup_tasks(vault)
        today = date.today().strftime("%Y%m%d")
        run("start-day", vault,
            "--day", today,
            "--agenda", AGENDA_JSON,
            "--priorities", PRIORITIES_JSON)
        year, month = today[:4], today[4:6]
        content = (vault / "Daily log" / year / month / f"{today}.md").read_text(encoding="utf-8")
        tasks_section = md.get_section(content, "Tasks")
        assert "ONLINE-1_T1" in tasks_section
        assert "ONLINE-1_T2" in tasks_section

    def test_priorities_section(self, vault):
        setup_tasks(vault)
        today = date.today().strftime("%Y%m%d")
        run("start-day", vault,
            "--day", today,
            "--agenda", AGENDA_JSON,
            "--priorities", PRIORITIES_JSON)
        year, month = today[:4], today[4:6]
        content = (vault / "Daily log" / year / month / f"{today}.md").read_text(encoding="utf-8")
        priorities = md.get_section(content, "Priorities")
        assert "ONLINE-1_T1" in priorities
        assert "ONLINE-1_T2" in priorities

    def test_idempotent_does_not_overwrite(self, vault):
        today = date.today().strftime("%Y%m%d")
        run("start-day", vault,
            "--day", today,
            "--agenda", AGENDA_JSON,
            "--priorities", PRIORITIES_JSON)
        year, month = today[:4], today[4:6]
        note = vault / "Daily log" / year / month / f"{today}.md"
        # Add a note to check it's not overwritten
        content = note.read_text(encoding="utf-8")
        note.write_text(content + "\n<!-- sentinel -->", encoding="utf-8")

        r = run("start-day", vault,
                "--day", today,
                "--agenda", AGENDA_JSON,
                "--priorities", PRIORITIES_JSON)
        assert r.returncode == 0
        assert "<!-- sentinel -->" in note.read_text(encoding="utf-8")
