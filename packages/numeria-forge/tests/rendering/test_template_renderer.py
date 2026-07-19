from pathlib import Path

from numeria_forge.rendering import (
    TemplateEnvironment,
    TemplateRenderer,
)


def test_renderer_renders_template():
    template_root = (
        Path(__file__).parent.parent
        / "fixtures"
        / "templates"
    )

    renderer = TemplateRenderer(
        TemplateEnvironment(template_root)
    )

    text = renderer.render(
        "hello.md.j2",
        {
            "title": "Numeria",
            "name": "Derivative",
        },
    )

    assert "# Numeria" in text
    assert "Hello Derivative!" in text