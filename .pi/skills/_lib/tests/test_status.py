"""Tests de integración de status.py — muestra el foco actual."""

import json
from datetime import datetime

from conftest import skill_script, run_script
from vault import focus as focus_mod


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


TODAY = datetime.now().strftime("%Y%m%d")
TIME_NOW = datetime.now().strftime("%H:%M")
AGENDA_JSON = json.dumps({"start": "08:00", "end": "17:00", "breaks": [], "meetings": []})


def setup_focused_task(vault):
    run("create-org", vault, "--name", "Mango")
    run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
    run("create-ticket", vault,
        "--org", "Mango", "--project", "Kondo",
        "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
    run("create-task", vault,
        "--org", "Mango", "--ticket", "ONLINE-1",
        "--title", "T1", "--description", "D")
    run("start-day", vault, "--day", TODAY, "--agenda", AGENDA_JSON, "--priorities", "[]")
    run("focus", vault,
        "--path", "Mango/Tickets/Tasks/ONLINE-1_T1.md",
        "--type", "task",
        "--day", TODAY, "--time", TIME_NOW,
        "--focus-file", str(vault / ".focus"))


class TestStatus:
    def test_returns_ok_with_focus_data(self, vault):
        setup_focused_task(vault)
        r = run_script(skill_script("status"), "--vault-root", str(vault),
                       "--focus-file", str(vault / ".focus"))
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["ok"] is True
        assert data["focused"] is True
        assert "ONLINE-1_T1" in data["path"]
        assert data["type"] == "task"
        assert data["day"] == TODAY

    def test_returns_ok_no_focus(self, vault):
        r = run_script(skill_script("status"), "--vault-root", str(vault),
                       "--focus-file", str(vault / ".focus"))
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["ok"] is True
        assert data["focused"] is False

    def test_includes_task_status_when_task_focused(self, vault):
        setup_focused_task(vault)
        r = run_script(skill_script("status"), "--vault-root", str(vault),
                       "--focus-file", str(vault / ".focus"))
        data = json.loads(r.stdout)
        assert data["task_status"] == "en-curso"

    def test_no_task_status_when_non_task_focus(self, vault):
        """Foco en ticket: no hay task_status."""
        run("create-org", vault, "--name", "Mango")
        run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
        run("create-ticket", vault,
            "--org", "Mango", "--project", "Kondo",
            "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        run("start-day", vault, "--day", TODAY, "--agenda", AGENDA_JSON, "--priorities", "[]")
        run("focus", vault,
            "--path", "Mango/Tickets/ONLINE-1.md",
            "--type", "ticket",
            "--day", TODAY, "--time", TIME_NOW,
            "--focus-file", str(vault / ".focus"))
        r = run_script(skill_script("status"), "--vault-root", str(vault),
                       "--focus-file", str(vault / ".focus"))
        data = json.loads(r.stdout)
        assert data["focused"] is True
        assert data.get("task_status") is None
