from dataclasses import dataclass

from numeria_forge.compiler.context import CompilerContext


@dataclass(frozen=True)
class WorkspaceBuildResult:
    """Result of compiling an entire workspace."""

    package_results: tuple[CompilerContext, ...]

    @property
    def package_count(self) -> int:
        return len(self.package_results)

    @property
    def artifact_count(self) -> int:
        return sum(
            len(result.artifacts)
            for result in self.package_results
        )
