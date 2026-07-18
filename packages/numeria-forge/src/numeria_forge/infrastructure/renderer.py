from collections.abc import Mapping
from typing import Any

from numeria_forge.infrastructure.template_loader import TemplateLoader


class TemplateRenderer:
    """Renders Forge templates using structured context data."""

    def __init__(self, loader: TemplateLoader | None = None) -> None:
        self.loader = loader or TemplateLoader()

    def render(
        self,
        template_name: str,
        context: Mapping[str, Any],
    ) -> str:
        template = self.loader.get_template(template_name)
        return template.render(**context)
