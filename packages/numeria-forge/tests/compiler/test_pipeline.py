from pathlib import Path

from numeria_forge.compiler import Compiler
from numeria_forge.compiler.context import CompilerContext


class RecordingStage:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def run(self, context: CompilerContext) -> CompilerContext:
        self.calls.append(self.name)
        return context


def test_compiler_executes_stages_in_order(tmp_path: Path) -> None:
    calls: list[str] = []

    compiler = Compiler(
        stages=[
            RecordingStage("load", calls),
            RecordingStage("render", calls),
            RecordingStage("publish", calls),
        ]
    )

    context = compiler.compile(tmp_path)

    assert calls == ["load", "render", "publish"]
    assert context.source_directory == tmp_path