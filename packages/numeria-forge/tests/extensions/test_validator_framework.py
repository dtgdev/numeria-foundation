from typing import Any

import pytest

from numeria_forge.domain.validators import (
    Validator,
    ValidatorRegistry,
)
from numeria_forge.extensions import (
    ExtensionContext,
    ForgeRegistries,
)


class RequiredNameValidator(Validator):
    @property
    def name(self) -> str:
        return "required_name"

    def validate(self, value: Any) -> tuple[str, ...]:
        if not isinstance(value, dict):
            return ("Value must be a mapping.",)

        if not value.get("name"):
            return ("Name is required.",)

        return ()


def test_validator_registry_registers_and_runs_validator() -> None:
    registry = ValidatorRegistry()

    registry.register(
        RequiredNameValidator()
    )

    assert registry.names == (
        "required_name",
    )

    assert registry.validate(
        "required_name",
        {},
    ) == (
        "Name is required.",
    )

    assert registry.validate(
        "required_name",
        {"name": "Derivative"},
    ) == ()


def test_validator_registry_rejects_duplicate_names() -> None:
    registry = ValidatorRegistry()

    registry.register(
        RequiredNameValidator()
    )

    with pytest.raises(ValueError):
        registry.register(
            RequiredNameValidator()
        )


def test_validator_registry_rejects_unknown_name() -> None:
    registry = ValidatorRegistry()

    with pytest.raises(
        KeyError,
        match="Validator 'missing' is not registered",
    ):
        registry.lookup("missing")


def test_extension_context_registers_validator() -> None:
    context = ExtensionContext(
        registries=ForgeRegistries(),
    )

    context.register_validator(
        RequiredNameValidator()
    )

    assert context.registries.validators.names == (
        "required_name",
    )
