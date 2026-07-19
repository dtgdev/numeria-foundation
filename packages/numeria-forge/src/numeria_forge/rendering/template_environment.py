from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
)


class TemplateEnvironment:
    """
    Creates and configures the Jinja environment.
    """

    def __init__(self, template_root: Path):
        self.environment = Environment(
            loader=FileSystemLoader(template_root),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )