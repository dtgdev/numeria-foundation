from pathlib import Path

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.diagnostic import Diagnostic
from numeria_forge.compiler.report import CompilationReport
from numeria_forge.domain.canon import Canon, CanonEntity
from numeria_forge.knowledge.statistics import GraphStatistics
from numeria_forge.publishing import PublishResult


def test_report_success() -> None:
    report = CompilationReport()

    assert report.success


def test_graph_statistics_defaults_to_none() -> None:
    report = CompilationReport()

    assert report.graph_statistics is None
    assert report.to_dict()["graph_statistics"] is None


def test_graph_statistics_appear_in_to_dict_when_present() -> None:
    stats = GraphStatistics(
        node_count=3, edge_count=2, edge_type_counts={"REQUIRES": 2},
        orphaned_node_count=1, acyclic_relationship_types=("REQUIRES",),
    )
    report = CompilationReport(graph_statistics=stats)

    assert report.to_dict()["graph_statistics"] == stats.to_dict()


def test_graph_statistics_appear_in_the_human_readable_summary() -> None:
    stats = GraphStatistics(node_count=3, edge_count=2, orphaned_node_count=1)
    report = CompilationReport(graph_statistics=stats)

    summary = report.format_human_readable()

    assert "Knowledge graph: 3 node(s), 2 edge(s), 1 orphaned entity." in summary


def test_report_failure() -> None:
    report = CompilationReport(
        diagnostics=[
            Diagnostic(
                severity="error",
                code="ERR001",
                message="Boom",
            )
        ]
    )

    assert not report.success


def _entity(entity_id: str, entity_type: str) -> CanonEntity:
    return CanonEntity(
        id=entity_id,
        type=entity_type,
        source_path=Path(f"knowledge/x/{entity_id}/entity.yaml"),
        data={},
    )


def _relationship_entity(entity_id: str, entity_type: str) -> CanonEntity:
    # Canon.is_relationship is keyed off the source_path's directory
    # (`RELATIONSHIPS_DIRECTORY_NAME in source_path.parts`), not the
    # entity's `type` string -- match the real convention here.
    return CanonEntity(
        id=entity_id,
        type=entity_type,
        source_path=Path(f"knowledge/relationships/{entity_id}/entity.yaml"),
        data={},
    )


def test_duration_seconds_defaults_to_none_and_is_passed_through() -> None:
    assert CompilationReport().duration_seconds is None

    report = CompilationReport(duration_seconds=1.5)
    assert report.duration_seconds == 1.5
    assert report.to_dict()["duration_seconds"] == 1.5


def test_duration_appears_in_the_human_readable_summary() -> None:
    report = CompilationReport(duration_seconds=1.75)

    assert "in 1.75s" in report.format_human_readable()


def test_no_duration_omits_the_duration_phrase() -> None:
    report = CompilationReport()

    summary = report.format_human_readable()
    assert "Compiled 0 stage(s): " in summary
    assert " in " not in summary.splitlines()[0]


def test_from_context_computes_entity_counts_and_relationship_count(
    tmp_path: Path,
) -> None:
    canon = Canon(root=tmp_path)
    canon.entities["NUM-CHR-000001"] = _entity("NUM-CHR-000001", "Character")
    canon.entities["NUM-CHR-000002"] = _entity("NUM-CHR-000002", "Character")
    canon.entities["NUM-CON-000001"] = _entity("NUM-CON-000001", "Concept")
    canon.entities["NUM-REL-000001"] = _relationship_entity("NUM-REL-000001", "REQUIRES")

    context = CompilerContext(project_root=tmp_path)
    context.loaded_canon = canon

    report = CompilationReport.from_context(context)

    assert report.entity_counts == {"Character": 2, "Concept": 1}
    assert report.relationship_count == 1
    assert report.to_dict()["entity_counts"] == {"Character": 2, "Concept": 1}
    assert report.to_dict()["relationship_count"] == 1


def test_from_context_with_no_loaded_canon_reports_empty_counts(
    tmp_path: Path,
) -> None:
    context = CompilerContext(project_root=tmp_path)

    report = CompilationReport.from_context(context)

    assert report.entity_counts == {}
    assert report.relationship_count == 0


def test_from_context_computes_published_by_format(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)
    context.published_assets = [
        PublishResult(publisher="p", path=tmp_path / "a.yaml", media_type="yaml"),
        PublishResult(publisher="p", path=tmp_path / "b.yaml", media_type="yaml"),
        PublishResult(publisher="p", path=tmp_path / "c.md", media_type="markdown"),
    ]

    report = CompilationReport.from_context(context)

    assert report.published_by_format == {"markdown": 1, "yaml": 2}


def test_entity_counts_and_published_by_format_appear_in_human_readable(
    tmp_path: Path,
) -> None:
    canon = Canon(root=tmp_path)
    canon.entities["NUM-CHR-000001"] = _entity("NUM-CHR-000001", "Character")

    context = CompilerContext(project_root=tmp_path)
    context.loaded_canon = canon
    context.published_assets = [
        PublishResult(publisher="p", path=tmp_path / "a.yaml", media_type="yaml"),
    ]

    report = CompilationReport.from_context(context)
    summary = report.format_human_readable()

    assert "Canon: 1 Character, 0 relationship(s)." in summary
    assert "Published: 1 yaml." in summary
