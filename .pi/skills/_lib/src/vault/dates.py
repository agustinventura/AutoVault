"""Lógica pura de fechas para el asistente.

Todas las funciones reciben un `datetime` explícito (inyectable) para ser
testeables sin depender del reloj real. La capa de I/O que consulta el reloj
del sistema vive en `vault.now`.
"""

from __future__ import annotations

from datetime import datetime, timedelta

_WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def day_id(dt: datetime) -> str:
    """Identificador de día en formato ``YYYYMMDD`` (p. ej. ``20260625``)."""
    return dt.strftime("%Y%m%d")


def time_of_day(dt: datetime) -> str:
    """Hora en formato ``HH:MM`` (24h, con ceros a la izquierda)."""
    return dt.strftime("%H:%M")


def weekday(dt: datetime) -> str:
    """Día de la semana en inglés y minúsculas (``monday`` .. ``sunday``)."""
    return _WEEKDAYS[dt.weekday()]


def iso_week(dt: datetime) -> str:
    """Etiqueta de semana ISO ``AAAA-Www`` (p. ej. ``2026-W26``).

    El año ISO puede diferir del año natural en los bordes.
    """
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def week_label(dt: datetime) -> str:
    """Etiqueta corta de semana ISO para nombres de archivo (``W-NN``)."""
    return f"W-{dt.isocalendar().week:02d}"


def is_friday(dt: datetime) -> bool:
    """``True`` si ``dt`` cae en viernes."""
    return dt.weekday() == 4


def week_range_mon_fri(dt: datetime) -> tuple[datetime, datetime]:
    """Devuelve (lunes, viernes) de la semana de ``dt``, a medianoche.

    El rango lunes-viernes es el que se recopila para el resumen semanal.
    """
    midnight = datetime(dt.year, dt.month, dt.day)
    monday = midnight - timedelta(days=midnight.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday
