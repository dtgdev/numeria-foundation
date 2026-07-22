from numeria_forge.compiler.diagnostic import Diagnostic
from numeria_forge.compiler.report import CompilationReport
from numeria_forge.knowledge.statistics import GraphStatistics


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
