from pathlib import Path

from numeria_forge.compiler import (
    Compiler,
    CompilerContext,
    CompilerStage,
)


class DummyStage(CompilerStage):
    @property
    def name(self) -> str:
        return "dummy"

    def execute(
        self,
        context: CompilerContext,
    ) -> None:
        context.canon["visited"] = True


def test_compiler_runs_stage() -> None:
    compiler = Compiler(
        stages=[
            DummyStage(),
        ],
    )

    context = CompilerContext(
        project_root=Path("."),
    )

    result = compiler.compile(context)

    assert result.success
    assert context.canon["visited"] is True
