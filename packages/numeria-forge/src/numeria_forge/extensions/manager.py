from numeria_forge.extensions.context import ExtensionContext
from numeria_forge.extensions.extension import Extension


class ExtensionManager:
    """Registers and manages Forge extensions."""

    def __init__(self) -> None:
        self._extensions: dict[str, Extension] = {}

    def register(
        self,
        extension: Extension,
        context: ExtensionContext,
    ) -> None:
        if extension.name in self._extensions:
            raise ValueError(
                f"Extension '{extension.name}' is already registered."
            )

        extension.register(context)

        self._extensions[extension.name] = extension

    @property
    def extensions(self) -> tuple[Extension, ...]:
        return tuple(self._extensions.values())

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._extensions.keys())
