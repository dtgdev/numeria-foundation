from typing import Any

import pytest

from numeria_forge.extensions import (
    CompilerHookRegistry,
    ExtensionContext,
    ForgeRegistries,
    HookPoint,
)


def test_hook_registry_preserves_registration_order() -> None:
    registry = CompilerHookRegistry()

    registry.register(
        HookPoint.BEFORE_RENDER,
        "first",
        lambda context: None,
    )
    registry.register(
        HookPoint.BEFORE_RENDER,
        "second",
        lambda context: None,
    )

    assert registry.names_for(
        HookPoint.BEFORE_RENDER
    ) == (
        "first",
        "second",
    )


def test_hook_registry_rejects_duplicate_names() -> None:
    registry = CompilerHookRegistry()

    registry.register(
        HookPoint.AFTER_RENDER,
        "example",
        lambda context: None,
    )

    with pytest.raises(ValueError):
        registry.register(
            HookPoint.AFTER_RENDER,
            "example",
            lambda context: None,
        )


def test_hook_registry_runs_hooks() -> None:
    registry = CompilerHookRegistry()
    events: list[str] = []

    def first(context: Any) -> None:
        context.append("first")

    def second(context: Any) -> None:
        context.append("second")

    registry.register(
        HookPoint.BEFORE_PUBLISH,
        "first",
        first,
    )
    registry.register(
        HookPoint.BEFORE_PUBLISH,
        "second",
        second,
    )

    registry.run(
        HookPoint.BEFORE_PUBLISH,
        events,
    )

    assert events == [
        "first",
        "second",
    ]


def test_extension_context_registers_compiler_hook() -> None:
    context = ExtensionContext(
        registries=ForgeRegistries(),
    )

    context.register_compiler_hook(
        HookPoint.AFTER_LOAD_MANIFEST,
        "validate_manifest",
        lambda compiler_context: None,
    )

    assert context.registries.compiler_hooks.names_for(
        HookPoint.AFTER_LOAD_MANIFEST
    ) == (
        "validate_manifest",
    )
