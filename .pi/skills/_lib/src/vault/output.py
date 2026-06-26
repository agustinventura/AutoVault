"""Utilidad de salida para orquestadores: exit code + JSON por stdout."""

from __future__ import annotations

import json
import sys


def ok(message: str = "", **extra) -> None:
    """Imprime ``{ok: true, ...}`` y termina con exit 0."""
    print(json.dumps({"ok": True, "message": message, **extra}, ensure_ascii=False))
    sys.exit(0)


def fail(error: str, code: str) -> None:
    """Imprime ``{ok: false, error, code}`` y termina con exit 1."""
    print(json.dumps({"ok": False, "error": error, "code": code}, ensure_ascii=False))
    sys.exit(1)
