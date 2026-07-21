from numeria_forge.compiler import CompilerStage, CompilerContext


class RecordingStage(CompilerStage):

    def __init__(
        self,
        name: str,
        calls: list[str],
    ):
        self._name = name
        self.calls = calls

    @property
    def name(self):
        return self._name

    def execute(
        self,
        context: CompilerContext,
    ):
        self.calls.append(self._name)
        return context