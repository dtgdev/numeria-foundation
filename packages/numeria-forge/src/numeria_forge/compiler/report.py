from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.diagnostics import Diagnostic
from numeria_forge.diagnostics import Severity as DiagnosticSeverity
from numeria_forge.knowledge.statistics import GraphStatistics


@dataclass(slots=True, frozen=True)
class CompilationReport:
    """Summary of a Forge compilation."""

    stages_executed: int = 0

    characters_processed: int = 0

    assets_published: int = 0

    generated_assets: int = 0

    diagnostics: list[Diagnostic] = field(default_factory=list)

    # v0.17.0: populated from context.knowledge_model when present.
    # None (not an all-zero GraphStatistics) when compilation never
    # reached BuildKnowledgeModelStage, so a caller can tell "no graph
    # was built" apart from "the graph was empty."
    graph_statistics: GraphStatistics | None = None

    # v0.19.0 -- "Compiler Hardening": observability additions. None of
    # these change what a compile *does*; they only report more about
    # what it did.

    # Wall-clock time for the whole FoundationCompiler.compile() call,
    # measured by the caller (see foundation_compiler.py) and passed
    # in here rather than timed internally -- CompilationReport stays
    # a plain summary object with no side effects of its own.
    duration_seconds: float | None = None

    # Non-relationship Canon entities grouped by type (Character,
    # Concept, Scene, ...), from context.loaded_canon. Deliberately
    # generic rather than hardcoding a fixed set of categories --
    # "Story" has no literal Canon entity type (see
    # GenerateMissingAssetsStage's note on this), so a report that
    # hardcoded "Stories" would either always read zero or silently
    # mean something else (Scene/Book). Whatever types actually exist
    # in the Canon show up here, nothing invented.
    entity_counts: dict[str, int] = field(default_factory=dict)

    # Total relationship entities (REQUIRES, FOLLOWS_SCENE, ... all
    # combined) -- one flat count, not broken down by predicate, to
    # match the intended report shape (a per-predicate breakdown is
    # already available via graph_statistics.edge_type_counts).
    relationship_count: int = 0

    # Published assets grouped by PublishResult.media_type (e.g.
    # "yaml", "markdown", "json"), from context.published_assets.
    published_by_format: dict[str, int] = field(default_factory=dict)

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is DiagnosticSeverity.ERROR
        )

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is DiagnosticSeverity.WARNING
        )

    @property
    def success(self) -> bool:
        return not any(self._is_error(d) for d in self.diagnostics)

    @staticmethod
    def _is_error(diagnostic: Diagnostic) -> bool:
        severity = diagnostic.severity

        if isinstance(severity, DiagnosticSeverity):
            return severity is DiagnosticSeverity.ERROR

        return str(severity).lower() == "error"

    @classmethod
    def from_context(
        cls,
        context: CompilerContext,
        stages_executed: int = 0,
        duration_seconds: float | None = None,
    ) -> "CompilationReport":
        """Build a report by summarizing a compiled context."""

        knowledge_model = context.knowledge_model
        canon = context.loaded_canon

        entity_counts: dict[str, int] = {}
        relationship_count = 0

        if canon is not None:
            entity_counts = dict(
                sorted(Counter(e.type for e in canon.non_relationships()).items())
            )
            relationship_count = len(canon.relationships())

        published_by_format = dict(
            sorted(Counter(a.media_type for a in context.published_assets).items())
        )

        return cls(
            stages_executed=stages_executed,
            characters_processed=len(context.characters),
            assets_published=len(context.published_assets),
            generated_assets=len(context.generated_assets),
            diagnostics=list(context.diagnostics),
            graph_statistics=(
                GraphStatistics.from_model(knowledge_model)
                if knowledge_model is not None
                else None
            ),
            duration_seconds=duration_seconds,
            entity_counts=entity_counts,
            relationship_count=relationship_count,
            published_by_format=published_by_format,
        )

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "stages_executed": self.stages_executed,
            "duration_seconds": self.duration_seconds,
            "characters_processed": self.characters_processed,
            "assets_published": self.assets_published,
            "generated_assets": self.generated_assets,
            "entity_counts": self.entity_counts,
            "relationship_count": self.relationship_count,
            "published_by_format": self.published_by_format,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "graph_statistics": (
                self.graph_statistics.to_dict()
                if self.graph_statistics is not None
                else None
            ),
            "diagnostics": [
                {
                    "severity": diagnostic.severity.value,
                    "code": diagnostic.code,
                    "message": diagnostic.message,
                    "location": (
                        str(diagnostic.location)
                        if diagnostic.location is not None
                        else None
                    ),
                }
                for diagnostic in self.diagnostics
            ],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def format_human_readable(self) -> str:
        duration = (
            f" in {self.duration_seconds:.2f}s"
            if self.duration_seconds is not None
            else ""
        )

        lines = [
            f"Compiled {self.stages_executed} stage(s){duration}: "
            f"{self.characters_processed} character(s) processed, "
            f"{self.generated_assets} asset(s) generated, "
            f"{self.assets_published} asset(s) published.",
        ]

        if self.entity_counts or self.relationship_count:
            counts = ", ".join(
                f"{count} {type_name}" for type_name, count in self.entity_counts.items()
            )
            lines.append(
                f"Canon: {counts}{', ' if counts else ''}"
                f"{self.relationship_count} relationship(s)."
            )

        if self.published_by_format:
            by_format = ", ".join(
                f"{count} {media_type}"
                for media_type, count in self.published_by_format.items()
            )
            lines.append(f"Published: {by_format}.")

        if self.graph_statistics is not None:
            stats = self.graph_statistics
            lines.append(
                f"Knowledge graph: {stats.node_count} node(s), "
                f"{stats.edge_count} edge(s), "
                f"{stats.orphaned_node_count} orphaned entit"
                f"{'y' if stats.orphaned_node_count == 1 else 'ies'}."
            )

        lines.append("")

        if not self.diagnostics:
            lines.append("No diagnostics.")
        else:
            for diagnostic in self.diagnostics:
                location = (
                    f" ({diagnostic.location})"
                    if diagnostic.location is not None
                    else ""
                )

                lines.append(
                    f"[{diagnostic.severity.value.upper()}] "
                    f"{diagnostic.code}: {diagnostic.message}{location}"
                )

            lines.append("")
            lines.append(
                f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)."
            )

        lines.append("Build succeeded." if self.success else "Build failed.")

        return "\n".join(lines)
