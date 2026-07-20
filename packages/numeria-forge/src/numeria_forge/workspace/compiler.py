from numeria_forge.compiler import Compiler
from numeria_forge.domain.workspaces import Workspace

from .build_result import WorkspaceBuildResult


class WorkspaceCompiler:
    """Compile every package in a workspace."""

    def __init__(self, compiler: Compiler):
        self.compiler = compiler

    def compile(
        self,
        workspace: Workspace,
    ) -> WorkspaceBuildResult:
        results = []

        for package in workspace.packages:
            package_directory = (
                workspace.root_directory
                / package.path
            )

            results.append(
                self.compiler.compile(package_directory)
            )

        return WorkspaceBuildResult(
            package_results=tuple(results)
        )
