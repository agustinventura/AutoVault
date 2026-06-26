#!/usr/bin/env bash
# Bootstrap del entorno del asistente de productividad diaria (auto_vault).
#
# Crea el entorno virtual único en .pi/skills/.venv e instala la librería
# compartida `vault` en modo editable. Ejecución manual y única (re-ejecutable
# de forma idempotente: recrea el venv si hace falta).
#
# Requisitos previos: uv (https://docs.astral.sh/uv/).
#
# Uso:
#   ./bootstrap.sh
set -euo pipefail

# Raíz del vault = directorio de este script.
VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${VAULT_ROOT}/.pi/skills"
VENV_DIR="${SKILLS_DIR}/.venv"
LIB_DIR="${SKILLS_DIR}/_lib"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 'uv' no está instalado o no está en el PATH." >&2
  echo "Instálalo con: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

echo "==> Creando entorno virtual en ${VENV_DIR}"
uv venv "${VENV_DIR}"

echo "==> Instalando la librería 'vault' (editable) con dependencias de desarrollo"
VIRTUAL_ENV="${VENV_DIR}" uv pip install -e "${LIB_DIR}[dev]"

echo ""
echo "Bootstrap completado."
echo "Intérprete:  ${VENV_DIR}/bin/python"
echo "Tests:       ${VENV_DIR}/bin/python -m pytest ${SKILLS_DIR}"
