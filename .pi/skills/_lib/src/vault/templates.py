"""Lectura de plantillas Markdown y sustitución de placeholders ``{{token}}``.

El delimitador doble ``{{ }}`` (estilo mustache) es el convenio del vault.
No colisiona con la sintaxis de Dataview inline ``{field}``.
"""

from __future__ import annotations

import re
from pathlib import Path

_TOKEN_RE = re.compile(r"\{\{(\w+)\}\}")


def render(text: str, context: dict[str, str]) -> str:
    """Sustituye todos los ``{{token}}`` de ``text`` con los valores de ``context``.

    Lanza ``KeyError`` si falta algún token.
    """
    def _replace(m: re.Match) -> str:
        key = m.group(1)
        if key not in context:
            raise KeyError(f"Token no encontrado en el contexto: {key!r}")
        return str(context[key])

    return _TOKEN_RE.sub(_replace, text)


def apply_template(template_path: Path, context: dict[str, str]) -> str:
    """Lee la plantilla y devuelve el texto con los tokens sustituidos.

    Lanza ``FileNotFoundError`` si la plantilla no existe.
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
    raw = template_path.read_text(encoding="utf-8")
    return render(raw, context)


def copy_template(
    template_path: Path,
    dest: Path,
    context: dict[str, str],
    overwrite: bool = False,
) -> None:
    """Aplica la plantilla y escribe el resultado en ``dest``.

    - Crea los directorios intermedios automáticamente.
    - Lanza ``FileExistsError`` si ``dest`` existe y ``overwrite`` es ``False``.
    """
    if dest.exists() and not overwrite:
        raise FileExistsError(f"El destino ya existe: {dest}")
    content = apply_template(template_path, context)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
