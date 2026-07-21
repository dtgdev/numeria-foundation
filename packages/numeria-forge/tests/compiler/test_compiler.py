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
    ) -> CompilerContext:
        context.diagnostics.append("dummy")
        return context


def test_compiler_runs_all_stages() -> None:
    compiler = Compiler(
        stages=[
            DummyStage(),
            DummyStage(),
        ],
    )

    context = compiler.compile(
        CompilerContext(
            project_name="Numeria",
        )
    )

    assert context.diagnostics == [
        "dummy",
        "dummy",
    ]
