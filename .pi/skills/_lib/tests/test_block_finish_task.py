"""Tests de integración de block_task.py y finish_task.py."""

import json
from datetime import datetime

from conftest import skill_script, run_script
from vault import markdown as md


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


AGENDA_JSON = json.dumps({"start": "08:00", "end": "17:00", "breaks": [], "meetings": []})
TODAY = datetime.now().strftime("%Y%m%d")
TIME_NOW = datetime.now().strftime("%H:%M")
TASK_PATH = "Mango/Tickets/Tasks/ONLINE-1_T1.md"


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
        "--path", TASK_PATH, "--type", "task",
        "--day", TODAY, "--time", TIME_NOW,
        "--focus-file", str(vault / ".focus"))


class TestBlockTask:
    def test_marks_task_bloqueada(self, vault):
        setup_focused_task(vault)
        r = run("block-task", vault,
                "--focus-file", str(vault / ".focus"),
                "--reason", "Esperando respuesta del equipo backend",
                "--day", TODAY, "--time", TIME_NOW)
        assert r.returncode == 0
        content = (vault / TASK_PATH).read_text(encoding="utf-8")
        assert md.get_field(content, "status") == "bloqueada"

    def test_reason_in_notes(self, vault):
        setup_focused_task(vault)
        run("block-task", vault,
            "--focus-file", str(vault / ".focus"),
            "--reason", "Bloqueado por X",
            "--day", TODAY, "--time", TIME_NOW)
        content = (vault / TASK_PATH).read_text(encoding="utf-8")
        assert "Bloqueado por X" in md.get_section(content, "Notas")

    def test_fails_without_task_focus(self, vault):
        setup_focused_task(vault)
        from vault import focus as fm
        fm.clear_focus(vault / ".focus")
        r = run("block-task", vault,
                "--focus-file", str(vault / ".focus"),
                "--reason", "X",
                "--day", TODAY, "--time", TIME_NOW)
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "NO_TASK_FOCUS"


class TestFinishTask:
    def test_marks_task_terminada(self, vault):
        setup_focused_task(vault)
        r = run("finish-task", vault,
                "--focus-file", str(vault / ".focus"),
                "--conclusion", "Tarea completada correctamente",
                "--day", TODAY, "--time", TIME_NOW)
        assert r.returncode == 0
        content = (vault / TASK_PATH).read_text(encoding="utf-8")
        assert md.get_field(content, "status") == "terminada"

    def test_sets_done_date(self, vault):
        setup_focused_task(vault)
        run("finish-task", vault,
            "--focus-file", str(vault / ".focus"),
            "--conclusion", "Hecho",
            "--day", TODAY, "--time", TIME_NOW)
        content = (vault / TASK_PATH).read_text(encoding="utf-8")
        assert md.get_field(content, "done") is not None

    def test_conclusion_in_notes(self, vault):
        setup_focused_task(vault)
        run("finish-task", vault,
            "--focus-file", str(vault / ".focus"),
            "--conclusion", "Conclusión de la tarea",
            "--day", TODAY, "--time", TIME_NOW)
        content = (vault / TASK_PATH).read_text(encoding="utf-8")
        assert "Conclusión de la tarea" in md.get_section(content, "Notas")

    def test_clears_focus(self, vault):
        setup_focused_task(vault)
        run("finish-task", vault,
            "--focus-file", str(vault / ".focus"),
            "--conclusion", "Done",
            "--day", TODAY, "--time", TIME_NOW)
        from vault import focus as fm
        assert fm.read_focus(vault / ".focus") is None

    def test_fails_without_task_focus(self, vault):
        setup_focused_task(vault)
        from vault import focus as fm
        fm.clear_focus(vault / ".focus")
        r = run("finish-task", vault,
                "--focus-file", str(vault / ".focus"),
                "--conclusion", "X",
                "--day", TODAY, "--time", TIME_NOW)
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "NO_TASK_FOCUS"
