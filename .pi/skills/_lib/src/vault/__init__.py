"""Librería compartida del asistente de productividad diaria (auto_vault).

Provee primitivas deterministas para que los orquestadores de las skills
manipulen el vault: construcción de rutas, lectura/escritura de Markdown y
frontmatter, máquina de estados de tareas, fechas, plantillas, wikilinks,
estado de foco y captura de notas.

Las acciones deterministas viven aquí; los orquestadores (scripts de cada
skill) las componen. El agente nunca realiza manualmente lo que un script
puede hacer.
"""

__version__ = "0.1.0"
