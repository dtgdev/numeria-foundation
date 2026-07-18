from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound


class TemplateLoader:
    """Loads Forge templates from the installed package."""

    def __init__(self, template_root: Path | None = None) -> None:
        self.template_root = template_root or (
            Path(__file__).resolve().parent.parent / "templates"
        )

        self.environment = Environment(
            loader=FileSystemLoader(self.template_root),
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
        )

    def get_template(self, template_name: str):
        try:
            return self.environment.get_template(template_name)
        except TemplateNotFound as error:
            raise FileNotFoundError(
                f"Forge template not found: {template_name}"
            ) from error