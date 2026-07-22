"""`forge init` -- scaffold a new Numeria Foundation.

Rewritten from its original form, which predated `numeria.yaml`, the
Canon domain model, and Canon Law #1-4 entirely: it used to create
`characters/`, `stories/`, `lessons/`, `assessments/` at the
**repository root** (not under `knowledge/`), and wrote a bespoke
`.numeria` marker file instead of a `numeria.yaml` manifest. Running it
against today's `FoundationLoader`/`CanonLoader` would produce a
directory tree those components can't actually read -- `forge
validate`/`forge compile` immediately after `forge init` would fail on
a missing `numeria.yaml`. This version scaffolds a Foundation that
`forge validate` and `forge compile` can load and validate immediately
(as an empty, but internally consistent, Canon).
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()

#: Directories created under `knowledge/`, one per Canon entity type
#: category (see docs/architecture/CANON_MODEL.md's PREFIX_BY_TYPE and
#: the project's own "Canon Architecture" breakdown: Characters,
#: Concepts, Realms, Stories, Scenes, Lessons, Assessments,
#: Relationships, Artifacts). `ontology/` is seeded separately below,
#: since it needs a starter file, not just an empty directory.
CANON_DIRECTORIES: tuple[str, ...] = (
    "characters",
    "concepts",
    "realms",
    "regions",
    "locations",
    "organizations",
    "events",
    "stories",
    "scenes",
    "books",
    "lessons",
    "assessments",
    "activities",
    "learning-objectives",
    "learning-journeys",
    "artifacts",
    "world",
    "relationships",
)

DEFAULT_ONTOLOGY = """\
version: "1.0.0"
status: CANON

# Every relationship type your Canon uses must be declared here --
# RelationshipValidator (part of `forge validate`) rejects any
# relationship entity whose `type` isn't listed. `source`/`target`
# restrict which entity types that relationship can connect; `acyclic:
# true` additionally means the dependency graph built from every
# relationship of that type must never form a cycle (see
# docs/architecture/SEMANTIC_LAYER.md). REQUIRES is included below as
# a working example -- delete it, or add your own types alongside it.
relationship_types:
  REQUIRES:
    source: Concept
    target: Concept
    acyclic: true
"""


def _numeria_yaml(foundation_id: str, foundation_name: str) -> str:
    return f"""\
schema_version: "1.0"

foundation:
  id: {foundation_id}
  name: {foundation_name}
  version: "0.1.0"

knowledge_root: knowledge

workspaces: []
"""


def init_repository(
    path: Path = typer.Argument(
        Path("."),
        help="Directory to initialize as a Numeria Foundation.",
    ),
    foundation_id: str = typer.Option(
        "my-foundation",
        "--id",
        help="Foundation id written into numeria.yaml.",
    ),
    foundation_name: str = typer.Option(
        "My Numeria Foundation",
        "--name",
        help="Foundation display name written into numeria.yaml.",
    ),
) -> None:
    """Initialize or verify a Numeria Foundation (numeria.yaml + knowledge/)."""

    root = path.resolve()
    knowledge_root = root / "knowledge"
    created: list[str] = []

    for relative_directory in CANON_DIRECTORIES:
        directory = knowledge_root / relative_directory

        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(f"knowledge/{relative_directory}/")

    ontology_path = knowledge_root / "ontology" / "relationship-types.yaml"

    if not ontology_path.is_file():
        ontology_path.parent.mkdir(parents=True, exist_ok=True)
        ontology_path.write_text(DEFAULT_ONTOLOGY, encoding="utf-8")
        created.append("knowledge/ontology/relationship-types.yaml")

    manifest_path = root / "numeria.yaml"

    if not manifest_path.is_file():
        manifest_path.write_text(
            _numeria_yaml(foundation_id, foundation_name),
            encoding="utf-8",
        )
        created.append("numeria.yaml")

    console.print()

    if created:
        console.print("[bold green]Numeria Foundation initialized.[/bold green]")
        console.print(f"[dim]Location:[/dim] {root}")
        console.print()
        console.print("[bold]Created:[/bold]")

        for item in created:
            console.print(f"  [green]+[/green] {item}")

        console.print()
        console.print(
            "Run [bold]forge validate[/bold] to check the (currently empty) "
            "Canon, or add `entity.yaml` files under knowledge/ and run it "
            "again."
        )
    else:
        console.print(
            "[yellow]Nothing to do -- this is already an initialized "
            "Numeria Foundation.[/yellow]"
        )
        console.print(f"[dim]Location:[/dim] {root}")
