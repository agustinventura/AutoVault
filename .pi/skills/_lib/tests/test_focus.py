"""Tests de integración de focus.py."""

import json
from datetime import datetime

from conftest import skill_script, run_script
from vault import markdown as md, focus as focus_mod
from pathlib import Path


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


AGENDA_JSON = json.dumps({
    "start": "08:00", "end": "17:00", "breaks": [], "meetings": []
})
TODAY = datetime.now().strftime("%Y%m%d")
TIME_NOW = datetime.now().strftime("%H:%M")


def setup_day_and_task(vault):
    run("create-org", vault, "--name", "Mango")
    run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
    run("create-ticket", vault,
        "--org", "Mango", "--project", "Kondo",
        "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
    run("create-task", vault,
        "--org", "Mango", "--ticket", "ONLINE-1",
        "--title", "T1", "--description", "D")
    run("start-day", vault,
        "--day", TODAY, "--agenda", AGENDA_JSON, "--priorities", "[]")


class TestFocus:
    def test_focuses_task_sets_en_curso(self, vault):
        setup_day_and_task(vault)
        task_path = "Mango/Tickets/Tasks/ONLINE-1_T1.md"
        r = run("focus", vault,
                "--path", task_path,
                "--type", "task",
                "--day", TODAY,
                "--time", TIME_NOW,
                "--focus-file", str(vault / ".focus"))
        assert r.returncode == 0
        content = (vault / task_path).read_text(encoding="utf-8")
        assert md.get_field(content, "status") == "en-curso"

    def test_focus_writes_focus_file(self, vault):
        setup_day_and_task(vault)
        task_path = "Mango/Tickets/Tasks/ONLINE-1_T1.md"
        run("focus", vault,
            "--path", task_path,
            "--type", "task",
            "--day", TODAY,
            "--time", TIME_NOW,
            "--focus-file", str(vault / ".focus"))
        data = focus_mod.read_focus(vault / ".focus")
        assert data is not None
        assert data["path"] == task_path
        assert data["type"] == "task"

    def test_focus_adds_day_anchor_to_task_notes(self, vault):
        setup_day_and_task(vault)
        task_path = "Mango/Tickets/Tasks/ONLINE-1_T1.md"
        run("focus", vault,
            "--path", task_path,
            "--type", "task",
            "--day", TODAY,
            "--time", TIME_NOW,
            "--focus-file", str(vault / ".focus"))
        content = (vault / task_path).read_text(encoding="utf-8")
        assert f"[[{TODAY}]]" in md.get_section(content, "Notas")

    def test_focus_adds_worked_today(self, vault):
        setup_day_and_task(vault)
        task_path = "Mango/Tickets/Tasks/ONLINE-1_T1.md"
        run("focus", vault,
            "--path", task_path,
            "--type", "task",
            "--day", TODAY,
            "--time", TIME_NOW,
            "--focus-file", str(vault / ".focus"))
        year, month = TODAY[:4], TODAY[4:6]
        daily = (vault / "Daily log" / year / month / f"{TODAY}.md").read_text(encoding="utf-8")
        assert "[[ONLINE-1_T1]]" in md.get_section(daily, "Trabajado hoy")

    def test_focus_fails_without_daily(self, vault):
        run("create-org", vault, "--name", "Mango")
        run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
        run("create-ticket", vault,
            "--org", "Mango", "--project", "Kondo",
            "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        run("create-task", vault,
            "--org", "Mango", "--ticket", "ONLINE-1",
            "--title", "T1", "--description", "D")
        r = run("focus", vault,
                "--path", "Mango/Tickets/Tasks/ONLINE-1_T1.md",
                "--type", "task",
                "--day", TODAY,
                "--time", TIME_NOW,
                "--focus-file", str(vault / ".focus"))
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "NO_DAILY"

    def test_focus_non_task_does_not_change_status(self, vault):
        """Focalizar un ticket no cambia ningún estado."""
        setup_day_and_task(vault)
        ticket_path = "Mango/Tickets/ONLINE-1.md"
        r = run("focus", vault,
                "--path", ticket_path,
                "--type", "ticket",
                "--day", TODAY,
                "--time", TIME_NOW,
                "--focus-file", str(vault / ".focus"))
        assert r.returncode == 0
        content = (vault / ticket_path).read_text(encoding="utf-8")
        # Los tickets no tienen status
        assert md.get_field(content, "status") is None
