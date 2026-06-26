"""Tests de integración de end_day.py y end_week.py."""

import json
from datetime import datetime

from conftest import skill_script, run_script
from vault import markdown as md


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


AGENDA_JSON = json.dumps({"start": "08:00", "end": "17:00", "breaks": [], "meetings": []})
TODAY = datetime.now().strftime("%Y%m%d")


def setup_day(vault):
    run("start-day", vault, "--day", TODAY, "--agenda", AGENDA_JSON, "--priorities", "[]")


class TestEndDay:
    def test_writes_reflection_to_day_close_out(self, vault):
        setup_day(vault)
        r = run("end-day", vault,
                "--day", TODAY,
                "--reflection", "Día productivo, terminé T1",
                "--pending", json.dumps([]))
        assert r.returncode == 0
        year, month = TODAY[:4], TODAY[4:6]
        content = (vault / "Daily log" / year / month / f"{TODAY}.md").read_text(encoding="utf-8")
        assert "Día productivo" in md.get_section(content, "Day close out")

    def test_writes_pending_tasks_to_day_close_out(self, vault):
        run("create-org", vault, "--name", "Mango")
        run("create-project", vault, "--org", "Mango", "--name", "Kondo", "--description", "x")
        run("create-ticket", vault,
            "--org", "Mango", "--project", "Kondo",
            "--id", "ONLINE-1", "--title", "T", "--target", "X", "--description", "D")
        run("create-task", vault,
            "--org", "Mango", "--ticket", "ONLINE-1",
            "--title", "T1", "--description", "D")
        setup_day(vault)
        r = run("end-day", vault,
                "--day", TODAY,
                "--reflection", "Buen día",
                "--pending", json.dumps(["ONLINE-1_T1"]))
        assert r.returncode == 0
        year, month = TODAY[:4], TODAY[4:6]
        content = (vault / "Daily log" / year / month / f"{TODAY}.md").read_text(encoding="utf-8")
        assert "[[ONLINE-1_T1]]" in md.get_section(content, "Day close out")

    def test_fails_if_no_daily(self, vault):
        r = run("end-day", vault,
                "--day", TODAY,
                "--reflection", "X",
                "--pending", json.dumps([]))
        assert r.returncode != 0
        assert json.loads(r.stdout)["code"] == "NO_DAILY"


class TestEndWeek:
    def test_creates_weekly_summary(self, vault):
        setup_day(vault)
        week_label = "W-26"
        iso_week = "2026-W26"
        r = run("end-week", vault,
                "--day", TODAY,
                "--week-label", week_label,
                "--iso-week", iso_week,
                "--date-from", "2026-06-22",
                "--date-to", "2026-06-26",
                "--completed-tasks", json.dumps([]),
                "--tickets-summary", "Sin cambios en tickets",
                "--initiatives-summary", "Sin cambios en iniciativas",
                "--priorities", json.dumps(["Revisar ONLINE-1"]))
        assert r.returncode == 0
        year, month = TODAY[:4], TODAY[4:6]
        note = vault / "Daily log" / year / month / f"{week_label}.md"
        assert note.exists()

    def test_weekly_note_contains_summaries(self, vault):
        setup_day(vault)
        run("end-week", vault,
            "--day", TODAY,
            "--week-label", "W-26",
            "--iso-week", "2026-W26",
            "--date-from", "2026-06-22",
            "--date-to", "2026-06-26",
            "--completed-tasks", json.dumps(["T1 - completada"]),
            "--tickets-summary", "ONLINE-1 avanzó",
            "--initiatives-summary", "Nada",
            "--priorities", json.dumps(["Prioridad 1"]))
        year, month = TODAY[:4], TODAY[4:6]
        content = (vault / "Daily log" / year / month / "W-26.md").read_text(encoding="utf-8")
        assert "ONLINE-1 avanzó" in content
        assert "Prioridad 1" in content
