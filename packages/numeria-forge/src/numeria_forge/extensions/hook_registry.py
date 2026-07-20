from collections.abc import Callable
from typing import Any

from numeria_forge.extensions.hooks import HookPoint


CompilerHook = Callable[[Any], None]


class CompilerHookRegistry:
    """Stores compiler hooks by lifecycle point."""

    def __init__(self) -> None:
        self._hooks: dict[
            HookPoint,
            list[tuple[str, CompilerHook]],
        ] = {
            hook_point: []
            for hook_point in HookPoint
        }

    def register(
        self,
        hook_point: HookPoint,
        name: str,
        hook: CompilerHook,
    ) -> None:
        existing_names = self.names_for(hook_point)

        if name in existing_names:
            raise ValueError(
                f"Compiler hook '{name}' is already registered "
                f"for '{hook_point.value}'."
            )

        self._hooks[hook_point].append(
            (name, hook)
        )

    def hooks_for(
        self,
        hook_point: HookPoint,
    ) -> tuple[CompilerHook, ...]:
        return tuple(
            hook
            for _, hook in self._hooks[hook_point]
        )

    def names_for(
        self,
        hook_point: HookPoint,
    ) -> tuple[str, ...]:
        return tuple(
            name
            for name, _ in self._hooks[hook_point]
        )

    def run(
        self,
        hook_point: HookPoint,
        context: Any,
    ) -> None:
        for hook in self.hooks_for(hook_point):
            hook(context)
