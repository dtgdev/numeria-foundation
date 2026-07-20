from pathlib import Path


class TemplateRegistry:
    """Registry of template roots contributed by extensions."""

    def __init__(self) -> None:
        self._roots: list[Path] = []

    def register(self, root: Path) -> None:
        if root not in self._roots:
            self._roots.append(root)

    @property
    def roots(self) -> tuple[Path, ...]:
        return tuple(self._roots)
