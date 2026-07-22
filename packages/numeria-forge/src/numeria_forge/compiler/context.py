from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from numeria_forge.diagnostics import Diagnostic
from numeria_forge.diagnostics import Severity as DiagnosticSeverity
from numeria_forge.domain.artifacts import ArtifactCollection
from numeria_forge.publishing import PublishResult


@dataclass(slots=True)
class CompilerContext:
    """Shared mutable state passed through the compiler pipeline."""

    project_root: Path

    source_directory: Path | None = None

    project: Any | None = None

    manifest: Any | None = None

    loaded_canon: Any | None = None

    artifact_registry: Any | None = None

    artifacts: ArtifactCollection = field(default_factory=ArtifactCollection)

    canon: dict[str, Any] = field(default_factory=dict)

    characters: list[Any] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    output_directory: Path | None = None

    build_directory: Path | None = None

    diagnostics: list[Diagnostic] = field(default_factory=list)

    generated_assets: list[Any] = field(default_factory=list)

    published_assets: list[PublishResult] = field(default_factory=list)

    # Populated by DependencyGraphStage / TopologicalOrderStage
    # (v0.15.0). Typed loosely (Any / bare tuple), matching
    # `loaded_canon`'s existing style, rather than importing
    # `numeria_forge.semantics.SemanticGraph` here -- CompilerContext
    # stays a plain data holder that doesn't need to know the concrete
    # shape of what each stage produces.
    semantic_graph: Any | None = None

    topological_order: tuple[str, ...] = ()

    # Populated by BuildKnowledgeModelStage (v0.16.0). Typed loosely
    # for the same reason as `semantic_graph` above -- see
    # `numeria_forge.knowledge.CanonicalKnowledgeModel` for the
    # concrete shape.
    knowledge_model: Any | None = None

    def __post_init__(self) -> None:
        if self.source_directory is None:
            self.source_directory = self.project_root

    @property
    def success(self) -> bool:
        """True when no diagnostic recorded on this context is an error."""

        return not any(self._is_error(d) for d in self.diagnostics)

    @staticmethod
    def _is_error(diagnostic: Diagnostic) -> bool:
        severity = diagnostic.severity

        if isinstance(severity, DiagnosticSeverity):
            return severity is DiagnosticSeverity.ERROR

        return str(severity).lower() == "error"
