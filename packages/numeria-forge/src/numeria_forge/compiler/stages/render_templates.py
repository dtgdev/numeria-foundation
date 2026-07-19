from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.domain.artifacts import Artifact
from numeria_forge.rendering import TemplateEnvironment, TemplateRenderer


class RenderTemplatesStage:
    """Render every output declared in the loaded manifest."""

    def __init__(self, template_root: Path) -> None:
        self.renderer = TemplateRenderer(
            TemplateEnvironment(template_root)
        )

    def run(self, context: CompilerContext) -> CompilerContext:
        if context.manifest is None:
            raise RuntimeError(
                "RenderTemplatesStage requires a loaded manifest."
            )

        context.artifacts.clear()   # if your collection supports it

        for output in context.manifest.outputs:
            content = self.renderer.render(
                output.template,
                {
                    "entity": context.manifest.entity,
                    "manifest": context.manifest,
                },
            )

            context.artifacts.add(
                Artifact(
                    destination=Path(output.destination),
                    content=content,
                )
            )

        return context