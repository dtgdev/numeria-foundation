from pathlib import Path

from numeria_forge.compiler import (
    Compiler,
    CompilerContext,
    CompilerStage,
)


class TestStage(CompilerStage):

    @property
    def name(self) -> str:
        return "test"

    def run(
        self,
        context: CompilerContext,
    ) -> None:
        context.metadata["executed"] = True


def test_compiler_executes_stage(
    tmp_path: Path,
) -> None:

    compiler = Compiler(
        stages=[
            TestStage(),
        ]
    )

    context = CompilerContext(
        source_directory=tmp_path,
        build_directory=tmp_path / "build",
    )

    compiler.compile(context)

    assert context.metadata["executed"] is True
