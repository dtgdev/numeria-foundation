"""Top-level orchestrator: numeria.yaml -> ... -> Compilation Report.

Wires together the full pipeline:

    numeria.yaml
        |
        v
    Project Discovery      (FoundationLoader: manifest + workspaces)
        |
        v
    Load Canon              (LoadCanonStage)
        |
        v
    Schema / Relationship /
    Semantic Validation     (ValidateCanonStage -- ten CanonValidators)
        |
        v
    Dependency Graph         (DependencyGraphStage, v0.15.0)
        |
        v
    Topological Ordering     (TopologicalOrderStage, v0.15.0)
        |
        v
    Generate Missing Assets   (GenerateMissingAssetsStage, v0.15.0 --
                               renders readme/character_card directly
                               from every Canon entity)
        |
        v
    Publish                   (PublishGeneratedAssetsStage writes
                               those to build/canon|stories|lessons|
                               assessments/...; per-package manifest
                               output is published too, via
                               PublishArtifactsStage, next to each
                               manifest.yaml)
        |
        v
    Package                   (write_build_reports writes
                               build/reports/{compile.json,
                               diagnostics.json, diagnostics.md})
        |
        v
    Compilation Report

Canon loading, validation, graph-building, and ordering all run
foundation-wide, over every entity under `knowledge/`. Generation then
runs two ways: `GenerateMissingAssetsStage` renders default output
directly from every Canon entity (closing the gap that used to mean
"generation legitimately compiles zero packages against real
content"), and the pre-existing per-package pipeline
(`LoadManifestStage`/`RegisterBuiltinArtifactsStage`/
`RenderTemplatesStage`) still runs for every hand-authored
`manifest.yaml` found inside the declared workspaces. Both are
published to disk: generated assets under `build/`, package artifacts
next to their `manifest.yaml`.

There is no dedicated "website" output -- the target `build/` layout
sketches one, but nothing in this codebase generates a static site
today, and fabricating an empty `website/` directory would misrepresent
that as done. `Story` in the target layout is also not a literal Canon
entity type; `Scene` and `Book` (the closest narrative-adjacent types)
are routed to `build/stories/` -- see `GenerateMissingAssetsStage`.
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.compiler.build_reports import write_build_reports
from numeria_forge.compiler.compiler import Compiler
from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.foundation_result import FoundationCompilationResult
from numeria_forge.compiler.report import CompilationReport
from numeria_forge.compiler.stages import (
    DependencyGraphStage,
    GenerateMissingAssetsStage,
    LoadCanonStage,
    LoadManifestStage,
    PublishArtifactsStage,
    PublishGeneratedAssetsStage,
    RegisterBuiltinArtifactsStage,
    RenderTemplatesStage,
    TopologicalOrderStage,
    ValidateCanonStage,
)
from numeria_forge.domain.validators import ValidatorRegistry
from numeria_forge.infrastructure.foundation_loader import FoundationLoader


class FoundationCompiler:
    """Compile an entire Numeria Foundation from its root `numeria.yaml`."""

    def __init__(
        self,
        validators: ValidatorRegistry | None = None,
        template_root: Path | None = None,
        loader: FoundationLoader | None = None,
    ) -> None:
        self._validators = validators
        self._template_root = template_root
        self._loader = loader or FoundationLoader()

    def compile(self, foundation_root: Path) -> FoundationCompilationResult:
        manifest = self._loader.load(foundation_root)
        template_root = self._resolve_template_root(foundation_root)

        context = CompilerContext(
            project_root=foundation_root,
            source_directory=foundation_root,
            build_directory=foundation_root / "build",
        )

        stages_executed = 0

        LoadCanonStage(knowledge_root=manifest.knowledge_root).execute(context)
        stages_executed += 1

        ValidateCanonStage(validators=self._validators).execute(context)
        stages_executed += 1

        DependencyGraphStage().execute(context)
        stages_executed += 1

        TopologicalOrderStage().execute(context)
        stages_executed += 1

        package_results: list[CompilerContext] = []

        if context.success:
            GenerateMissingAssetsStage(template_root).execute(context)
            stages_executed += 1

            PublishGeneratedAssetsStage().execute(context)
            stages_executed += 1

            package_compiler = Compiler(
                stages=[
                    LoadManifestStage(),
                    RegisterBuiltinArtifactsStage(),
                    RenderTemplatesStage(template_root),
                    PublishArtifactsStage(),
                ]
            )

            for workspace_root in manifest.workspaces:
                if not workspace_root.is_dir():
                    continue

                for manifest_path in sorted(
                    workspace_root.rglob("manifest.yaml")
                ):
                    package_directory = manifest_path.parent

                    package_results.append(
                        package_compiler.compile(package_directory)
                    )

                    stages_executed += package_compiler.stage_count

        report = CompilationReport.from_context(
            context,
            stages_executed=stages_executed,
        )

        # "Package": write the Compilation Report to build/reports/
        # before returning it, matching Publish -> Package ->
        # Compilation Report in the target pipeline. Written even when
        # the Canon was invalid (context.success is False) -- that's
        # exactly when build/reports/diagnostics.md is most useful.
        write_build_reports(context.build_directory, report)

        return FoundationCompilationResult(
            context=context,
            report=report,
            package_results=tuple(package_results),
        )

    def _resolve_template_root(self, foundation_root: Path) -> Path:
        if self._template_root is not None:
            return self._template_root

        return foundation_root / "packages" / "numeria-forge" / "templates"
