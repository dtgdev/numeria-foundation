
"""Forge compiler."""

from __future__ import annotations

from numeria_forge.compiler.context import (

    CompilerContext,

)

from numeria_forge.compiler.report import (

    CompilationReport,

)

class Compiler:

    """Top-level Forge compiler."""

    def compile(

        self,

        context: CompilerContext,

    ) -> CompilationReport:

        """Compile a Numeria project."""

        return CompilationReport(

            success=not context.diagnostics,

            generated_assets=len(

                context.generated_assets

            ),

            published_assets=len(

                context.published_assets

            ),

            diagnostics=len(

                context.diagnostics

            ),

        )

