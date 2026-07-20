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

    @property
    def package_names(self) -> tuple[str, ...]:
        names = []

        for result in self.package_results:
            if result.manifest is None:
                continue

            names.append(result.manifest.entity.slug)

        return tuple(names)

    def format_report(self, workspace_name: str) -> str:
        lines = [
            f"Building {workspace_name}...",
            "",
        ]

        lines.extend(
            f"✓ {package_name}"
            for package_name in self.package_names
        )

        lines.extend(
            [
                "",
                f"{self.package_count} packages compiled",
                f"{self.artifact_count} artifacts generated",
                "",
                "Build succeeded.",
            ]
        )

        return "\n".join(lines)
