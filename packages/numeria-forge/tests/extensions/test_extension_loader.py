from unittest.mock import patch

from numeria_forge.extensions import Extension
from numeria_forge.extensions.loader import ExtensionLoader


class DemoExtension(Extension):

    @property
    def name(self) -> str:
        return "demo"

    def register(self, context) -> None:
        pass


class FakeEntryPoint:

    def __init__(self, name, obj):
        self.name = name
        self.value = f"{obj.__module__}:{obj.__name__}"
        self._obj = obj

    def load(self):
        return self._obj


@patch("numeria_forge.extensions.loader.entry_points")
def test_loader_discovers_extensions(mock_entry_points):

    mock_entry_points.return_value = [
        FakeEntryPoint("demo", DemoExtension),
    ]

    loader = ExtensionLoader()

    extensions = loader.discover()

    assert len(extensions) == 1
    assert extensions[0].name == "demo"
