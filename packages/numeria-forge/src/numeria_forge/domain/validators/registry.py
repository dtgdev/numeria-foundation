from typing import Any

from numeria_forge.domain.validators.validator import Validator


class ValidatorRegistry:
    """Registry of validators contributed by Forge Core and extensions."""

    def __init__(self) -> None:
        self._validators: dict[str, Validator] = {}

    def register(self, validator: Validator) -> None:
        if validator.name in self._validators:
            raise ValueError(
                f"Validator '{validator.name}' is already registered."
            )

        self._validators[validator.name] = validator

    def lookup(self, name: str) -> Validator:
        try:
            return self._validators[name]
        except KeyError as error:
            raise KeyError(
                f"Validator '{name}' is not registered."
            ) from error

    def validate(
        self,
        name: str,
        value: Any,
    ) -> tuple[str, ...]:
        return self.lookup(name).validate(value)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._validators.keys())
