# ADR-0004 — uv, venv único e invocación con intérprete absoluto

## Contexto
La librería editable (ADR-0003) requiere un entorno. El agente lanza scripts vía
bash, sin garantía de tener un venv activado.

## Decisión
- Gestor de entorno: **uv**.
- Entorno virtual **único** en `.pi/skills/.venv`, con `vault` instalado editable.
- Los scripts se invocan con la **ruta al intérprete del venv**, relativa a
  `cwd` (que es la raíz del vault):
  `.pi/skills/.venv/bin/python .pi/skills/<accion>/scripts/<x>.py`.

## Alternativas
- **`uv run`**: resuelve el venv automáticamente, pero apuntar a scripts de otra
  carpeta complica la resolución del proyecto.
- **Activar el venv / `PYTHONPATH`**: frágil si bash arranca sin entorno.
- **`venv` + `pip`** en vez de uv: más lento, sin lockfile reproducible.

## Consecuencias
- Cero activación: la ruta absoluta al intérprete basta.
- Un único entorno para todas las skills y los tests.
- `.venv` se git-ignora y se recrea con `bootstrap.sh`.
