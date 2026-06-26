"""Ejecutable: emite fecha/hora/semana del sistema como JSON.

Uso:
    python -m vault.now

Salida (stdout), por ejemplo:
    {"date": "20260625", "time": "10:14", "weekday": "thursday",
     "iso_week": "2026-W26", "week_label": "W-26", "is_friday": false}

Asume la hora local del sistema (asistente personal mono-usuario).
"""

from __future__ import annotations

import json
from datetime import datetime

from vault import dates


def payload(dt: datetime) -> dict:
    """Construye el diccionario de tiempo a partir de ``dt`` (pura)."""
    return {
        "date": dates.day_id(dt),
        "time": dates.time_of_day(dt),
        "weekday": dates.weekday(dt),
        "iso_week": dates.iso_week(dt),
        "week_label": dates.week_label(dt),
        "is_friday": dates.is_friday(dt),
    }


def main() -> None:
    print(json.dumps(payload(datetime.now()), ensure_ascii=False))


if __name__ == "__main__":
    main()
