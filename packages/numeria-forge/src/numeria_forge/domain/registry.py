from numeria_forge.domain.generators.base import BaseGenerator


class GeneratorRegistry:
    """Registry for all available generators."""

    def __init__(self) -> None:
        self._generators: dict[str, BaseGenerator] = {}

    def register(
        self,
        generator: BaseGenerator,
    ) -> None:
        self._generators[generator.name] = generator

    def get(self, name: str) -> BaseGenerator:
        if name not in self._generators:
            raise KeyError(f"Unknown generator: {name}")

        return self._generators[name]

    def names(self) -> list[str]:
        return sorted(self._generators.keys())
