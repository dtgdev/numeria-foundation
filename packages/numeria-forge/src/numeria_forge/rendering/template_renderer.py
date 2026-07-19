from numeria_forge.rendering.template_environment import TemplateEnvironment


class TemplateRenderer:
    """
    Render templates into text.
    """

    def __init__(self, environment: TemplateEnvironment):
        self.environment = environment.environment

    def render(
        self,
        template_name: str,
        context: dict,
    ) -> str:
        template = self.environment.get_template(template_name)
        return template.render(**context)