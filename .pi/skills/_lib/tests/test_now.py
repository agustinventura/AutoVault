"""Tests de vault.now — payload de fecha/hora y ejecutable JSON."""

import json
import subprocess
import sys
from datetime import datetime

from vault import now


class TestPayload:
    def test_builds_full_payload(self):
        dt = datetime(2026, 6, 25, 10, 14)
        assert now.payload(dt) == {
            "date": "20260625",
            "time": "10:14",
            "weekday": "thursday",
            "iso_week": "2026-W26",
            "week_label": "W-26",
            "is_friday": False,
        }

    def test_friday_flag(self):
        assert now.payload(datetime(2026, 6, 26, 9, 0))["is_friday"] is True


class TestExecutableModule:
    def test_python_m_vault_now_emits_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "vault.now"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Keys present and well-formed regardless of the real clock.
        assert set(data) == {
            "date",
            "time",
            "weekday",
            "iso_week",
            "week_label",
            "is_friday",
        }
        assert len(data["date"]) == 8
        assert ":" in data["time"]
