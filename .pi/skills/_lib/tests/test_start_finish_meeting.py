"""Tests de integración de start_meeting.py y finish_meeting.py."""

import json
from datetime import datetime

from conftest import skill_script, run_script
from vault import markdown as md, focus as focus_mod


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


AGENDA_JSON = json.dumps({
    "start": "08:00", "end": "17:00", "breaks": [],
    "meetings": [{"name": "Kondo Daily", "start": "09:45", "end": "10:00"}]
})
TODAY = datetime.now().strftime("%Y%m%d")
TIME_NOW = datetime.now().strftime("%H:%M")
TASK_PATH = "Mango/Tickets/Tasks/ONLINE-1_T1.md"


def setup_day(vault):
    run("create-org", vault, "--name", "Mango")
    run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
    run("create-ticket", vault,
        "--org", "Mango", "--project", "Kondo",
        "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
    run("create-task", vault,
        "--org", "Mango", "--ticket", "ONLINE-1",
        "--title", "T1", "--description", "D")
    run("start-day", vault, "--day", TODAY, "--agenda", AGENDA_JSON, "--priorities", "[]")


class TestStartMeeting:
    def test_creates_meeting_note(self, vault):
        setup_day(vault)
        r = run("start-meeting", vault,
                "--day", TODAY, "--time", TIME_NOW,
                "--org", "Mango", "--project", "Kondo",
                "--name", "Kondo Daily",
                "--participants", "Agustín, María",
                "--goal", "Sincronización del equipo",
                "--focus-file", str(vault / ".focus"))
        assert r.returncode == 0
        year, month = TODAY[:4], TODAY[4:6]
        note = vault / "Mango" / "Meetings" / year / month / f"{TODAY}-Kondo Daily.md"
        assert note.exists()

    def test_meeting_frontmatter(self, vault):
        setup_day(vault)
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        year, month = TODAY[:4], TODAY[4:6]
        content = (vault / "Mango" / "Meetings" / year / month / f"{TODAY}-Kondo Daily.md").read_text(encoding="utf-8")
        assert md.get_field(content, "type") == "meeting"
        assert md.get_field(content, "org") == "Mango"

    def test_injects_wikilink_in_agenda(self, vault):
        setup_day(vault)
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        year, month = TODAY[:4], TODAY[4:6]
        daily = (vault / "Daily log" / year / month / f"{TODAY}.md").read_text(encoding="utf-8")
        agenda = md.get_section(daily, "Agenda")
        assert f"[[{TODAY}-Kondo Daily]]" in agenda

    def test_task_in_focus_goes_to_pendiente(self, vault):
        setup_day(vault)
        run("focus", vault,
            "--path", TASK_PATH, "--type", "task",
            "--day", TODAY, "--time", TIME_NOW,
            "--focus-file", str(vault / ".focus"))
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        content = (vault / TASK_PATH).read_text(encoding="utf-8")
        assert md.get_field(content, "status") == "pendiente"

    def test_focus_set_to_meeting(self, vault):
        setup_day(vault)
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        data = focus_mod.read_focus(vault / ".focus")
        assert data is not None
        assert data["type"] == "meeting"

    def test_adds_to_project_enlaces(self, vault):
        setup_day(vault)
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        project = (vault / "Mango" / "Proyectos" / "Kondo" / "Kondo.md").read_text(encoding="utf-8")
        assert f"[[{TODAY}-Kondo Daily]]" in md.get_section(project, "Enlaces")

    def test_ad_hoc_meeting_inserts_in_agenda(self, vault):
        setup_day(vault)
        r = run("start-meeting", vault,
                "--day", TODAY, "--time", "15:20",
                "--org", "Mango", "--project", "Kondo",
                "--name", "Sync Rápido",
                "--participants", "Agustín",
                "--goal", "Urgente",
                "--focus-file", str(vault / ".focus"),
                "--ad-hoc")
        assert r.returncode == 0
        year, month = TODAY[:4], TODAY[4:6]
        daily = (vault / "Daily log" / year / month / f"{TODAY}.md").read_text(encoding="utf-8")
        assert "Sync Rápido" in md.get_section(daily, "Agenda")


class TestFinishMeeting:
    def test_adds_conclusions(self, vault):
        setup_day(vault)
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        r = run("finish-meeting", vault,
                "--focus-file", str(vault / ".focus"),
                "--conclusion", "Todo sincronizado")
        assert r.returncode == 0
        year, month = TODAY[:4], TODAY[4:6]
        content = (vault / "Mango" / "Meetings" / year / month / f"{TODAY}-Kondo Daily.md").read_text(encoding="utf-8")
        assert "Todo sincronizado" in md.get_section(content, "Conclusiones")

    def test_clears_focus_after_meeting(self, vault):
        setup_day(vault)
        run("start-meeting", vault,
            "--day", TODAY, "--time", TIME_NOW,
            "--org", "Mango", "--project", "Kondo",
            "--name", "Kondo Daily",
            "--participants", "Agustín",
            "--goal", "Sync",
            "--focus-file", str(vault / ".focus"))
        run("finish-meeting", vault,
            "--focus-file", str(vault / ".focus"),
            "--conclusion", "Done")
        assert focus_mod.read_focus(vault / ".focus") is None
