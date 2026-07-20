"""Extension manager."""

from __future__ import annotations

from numeria_forge.extensions.context import ExtensionContext
from numeria_forge.extensions.extension import Extension
from numeria_forge.extensions.loader import ExtensionLoader


class ExtensionManager:
    """Manage Forge extensions."""

    def __init__(self) -> None:
        self._extensions: dict[str, Extension] = {}

    @property
    def names(self) -> tuple[str, ...]:
        """Return registered extension names."""

        return tuple(sorted(self._extensions))

    @property
    def extensions(self) -> tuple[Extension, ...]:
        """Return registered extensions."""

        return tuple(
            self._extensions[name]
            for name in sorted(self._extensions)
        )

    def register(
        self,
        extension: Extension,
        context: ExtensionContext,
    ) -> None:
        """Register an extension."""

        if extension.name in self._extensions:
            raise ValueError(
                f"Extension '{extension.name}' is already registered."
            )

        extension.register(context)

        self._extensions[extension.name] = extension

    def load_installed(
        self,
        context: ExtensionContext,
        loader: ExtensionLoader | None = None,
    ) -> None:
        """Discover and register installed extensions."""

        loader = loader or ExtensionLoader()

        for extension in loader.discover():
            self.register(
                extension,
                context,
            )
