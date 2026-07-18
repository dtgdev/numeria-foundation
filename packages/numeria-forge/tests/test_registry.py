from pathlib import Path
from typing import Any

import pytest

from numeria_forge.domain.generators.base import BaseGenerator
from numeria_forge.domain.registry import GeneratorRegistry


class DummyGenerator(BaseGenerator):
    name = "dummy"

    def generate(
        self,
        output_directory: Path,
        context: dict[str, Any],
    ) -> list[Path]:
        return []


def test_register_generator() -> None:
    registry = GeneratorRegistry()

    registry.register(DummyGenerator())

    assert registry.names() == ["dummy"]


def test_lookup_generator() -> None:
    registry = GeneratorRegistry()
    generator = DummyGenerator()

    registry.register(generator)

    assert registry.get("dummy") is generator


def test_unknown_generator() -> None:
    registry = GeneratorRegistry()

    with pytest.raises(KeyError, match="Unknown generator: missing"):
        registry.get("missing")
