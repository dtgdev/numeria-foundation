from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.domain.artifacts import (
    Artifact,
    create_builtin_registry,
)
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

        registry = create_builtin_registry()

        context.artifacts.clear()

        for output in context.manifest.outputs:
            if output.artifact is not None:
                definition = registry.lookup(output.artifact)

                template = definition.template
                destination = (
                    output.destination
                    or definition.default_destination
                )
            else:
                template = output.template
                destination = output.destination

            if template is None or destination is None:
                raise RuntimeError(
                    "Manifest output could not be resolved to a "
                    "template and destination."
                )

            content = self.renderer.render(
                template,
                {
                    "entity": context.manifest.entity,
                    "manifest": context.manifest,
                },
            )

            context.artifacts.add(
                Artifact(
                    destination=Path(destination),
                    content=content,
                )
            )

        return context