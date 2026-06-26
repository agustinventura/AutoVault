"""Fixtures y helpers compartidos para los tests de integración."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# auto_vault/ está 4 niveles arriba de tests/
# tests/ → _lib/ → skills/ → .pi/ → auto_vault/
_VAULT_ROOT = Path(__file__).parents[4]
_TEMPLATES_SRC = _VAULT_ROOT / "Templates"
_SKILLS_ROOT = Path(__file__).parents[2]  # tests/ → _lib/ → skills/


@pytest.fixture()
def vault(tmp_path: Path) -> Path:
    """Vault temporal con las plantillas reales copiadas.

    Devuelve la ruta raíz del vault temporal.
    Los tests de integración deben usar este fixture como raíz.
    """
    templates_dst = tmp_path / "Templates"
    shutil.copytree(_TEMPLATES_SRC, templates_dst)
    return tmp_path


def skill_script(skill_name: str) -> Path:
    """Ruta al script orquestador de una skill (por el nombre de la skill sin prefijo).

    Ejemplo: skill_script("create-org") →
        .pi/skills/daily-flow-create-org/scripts/create_org.py
    """
    py_name = skill_name.replace("-", "_") + ".py"
    return _SKILLS_ROOT / f"daily-flow-{skill_name}" / "scripts" / py_name


def run_script(script_path: Path, *args: str) -> subprocess.CompletedProcess:
    """Ejecuta un script orquestador con el intérprete del venv."""
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
    )
