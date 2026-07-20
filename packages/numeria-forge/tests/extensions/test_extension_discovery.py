from numeria_forge.extensions import (
    Extension,
    ExtensionContext,
    ExtensionManager,
    ForgeRegistries,
)
from numeria_forge.extensions.loader import ExtensionLoader


class DemoExtension(Extension):
    @property
    def name(self) -> str:
        return "demo"

    def register(self, context: ExtensionContext) -> None:
        pass


class FakeLoader(ExtensionLoader):
    def discover(self) -> list[Extension]:
        return [
            DemoExtension(),
        ]


def test_manager_load_installed() -> None:
    manager = ExtensionManager()

    context = ExtensionContext(
        registries=ForgeRegistries(),
    )

    manager.load_installed(
        context,
        loader=FakeLoader(),
    )

    assert manager.names == ("demo",)
