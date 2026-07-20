"""Automatic discovery of installed Numeria Forge extensions."""

from __future__ import annotations

from importlib.metadata import EntryPoint
from importlib.metadata import entry_points

from numeria_forge.extensions.extension import Extension


class ExtensionLoader:
    """Discover installed Forge extensions."""

    GROUP = "numeria_forge.extensions"

    def discover_entry_points(self) -> list[EntryPoint]:
        """Return Forge extension entry points."""

        return sorted(
            entry_points(group=self.GROUP),
            key=lambda ep: ep.name,
        )

    def load(self, entry_point: EntryPoint) -> Extension:
        """Load a single extension."""

        obj = entry_point.load()

        if isinstance(obj, type):
            obj = obj()

        if not isinstance(obj, Extension):
            raise TypeError(
                f"{entry_point.value} is not a Forge Extension."
            )

        return obj

    def discover(self) -> list[Extension]:
        """Discover all installed extensions."""

        return [
            self.load(entry_point)
            for entry_point in self.discover_entry_points()
        ]
