from pathlib import Path

import typer
from rich.console import Console

from numeria_forge import __version__
from numeria_forge.commands.init import init_repository

console = Console()

app = typer.Typer(
    name="forge",
    help="Forge mathematical worlds from canonical knowledge.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command("version")
def version_command() -> None:
    """Display the installed Numeria Forge version."""

    console.print(f"Numeria Forge [bold]{__version__}[/bold]")


app.command("init")(init_repository)


def _resolve_knowledge_root(path: "Path") -> "Path":
    """Resolve a knowledge root from a foundation root, a parent of
    `knowledge/`, or a knowledge root passed directly."""

    from numeria_forge.infrastructure.foundation_loader import FoundationLoader

    resolved = path.resolve()

    if (resolved / "numeria.yaml").is_file():
        return FoundationLoader().load(resolved).knowledge_root

    if (resolved / "knowledge").is_dir():
        return resolved / "knowledge"

    return resolved


@app.command("validate")
def validate_command(
    path: "Path" = typer.Argument(
        None,
        help=(
            "Foundation root (containing numeria.yaml), a directory "
            "containing knowledge/, or a knowledge root itself. "
            "Defaults to the current directory."
        ),
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit the validation report as JSON instead of text.",
    ),
) -> None:
    """Validate the Canon and report whether it is internally consistent."""

    from pathlib import Path as _Path

    from numeria_forge.domain.canon.validation import CanonValidationRunner

    target = path if path is not None else _Path.cwd()
    knowledge_root = _resolve_knowledge_root(target)

    report = CanonValidationRunner().run(knowledge_root)

    if as_json:
        console.print_json(report.to_json())
    else:
        console.print(report.format_human_readable())

    if not report.success:
        raise typer.Exit(code=1)


@app.command("compile")
def compile_command(
    path: "Path" = typer.Argument(
        None,
        help=(
            "Foundation root (containing numeria.yaml). Defaults to "
            "the current directory."
        ),
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit the compilation report as JSON instead of text.",
    ),
) -> None:
    """Run the full pipeline: load canon, validate, generate, publish."""

    from pathlib import Path as _Path

    from numeria_forge.compiler import FoundationCompiler

    target = path if path is not None else _Path.cwd()

    result = FoundationCompiler().compile(target)

    if as_json:
        console.print_json(result.report.to_json())
    else:
        console.print(result.report.format_human_readable())

    if not result.success:
        raise typer.Exit(code=1)


@app.command("doctor")
def doctor_command(
    path: "Path" = typer.Argument(
        None,
        help=(
            "Foundation root (containing numeria.yaml). Defaults to "
            "the current directory."
        ),
    ),
) -> None:
    """Diagnose whether this Foundation is set up correctly.

    Runs a fast checklist -- Python version, numeria.yaml, knowledge
    root, ontology file, and a Canon load + validate pass -- and
    prints a pass/fail summary. This is a health check, not a
    replacement for `forge validate`: on a failing Canon, run
    `forge validate` for the actual diagnostics.
    """

    import sys
    from dataclasses import dataclass
    from pathlib import Path as _Path

    from numeria_forge import __version__
    from numeria_forge.domain.canon import CanonLoader
    from numeria_forge.domain.canon.validation import CanonValidationRunner
    from numeria_forge.infrastructure.foundation_loader import FoundationLoader

    @dataclass
    class DoctorCheck:
        name: str
        status: str  # "ok" | "warning" | "error"
        message: str

    target = (path if path is not None else _Path.cwd()).resolve()
    checks: list[DoctorCheck] = []

    required_python = (3, 11)
    if sys.version_info[:2] >= required_python:
        checks.append(
            DoctorCheck(
                "Python version",
                "ok",
                f"{sys.version_info.major}.{sys.version_info.minor} "
                f"(requires >= {required_python[0]}.{required_python[1]})",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "Python version",
                "error",
                f"{sys.version_info.major}.{sys.version_info.minor} is below "
                f"the required {required_python[0]}.{required_python[1]}",
            )
        )

    checks.append(DoctorCheck("Forge version", "ok", __version__))

    knowledge_root = None

    manifest_path = target / "numeria.yaml"
    if manifest_path.is_file():
        try:
            manifest = FoundationLoader().load(target)
        except ValueError as exc:
            checks.append(DoctorCheck("numeria.yaml", "error", str(exc)))
        else:
            checks.append(
                DoctorCheck(
                    "numeria.yaml",
                    "ok",
                    f"foundation '{manifest.metadata.id}' "
                    f"({manifest.metadata.version})",
                )
            )
            knowledge_root = manifest.knowledge_root
    else:
        checks.append(
            DoctorCheck(
                "numeria.yaml",
                "warning",
                "not found -- run `forge init`, or pass a knowledge root "
                "directly to `forge validate`/`forge compile`",
            )
        )

    if knowledge_root is None:
        knowledge_root = _resolve_knowledge_root(target)

    if knowledge_root.is_dir():
        checks.append(
            DoctorCheck("Knowledge root", "ok", str(knowledge_root))
        )
    else:
        checks.append(
            DoctorCheck(
                "Knowledge root",
                "error",
                f"{knowledge_root} does not exist",
            )
        )

    ontology_path = knowledge_root / "ontology" / "relationship-types.yaml"
    if ontology_path.is_file():
        checks.append(DoctorCheck("Ontology file", "ok", str(ontology_path)))
    else:
        checks.append(
            DoctorCheck(
                "Ontology file",
                "error",
                f"{ontology_path} not found -- RelationshipValidator "
                "requires this file unconditionally, even for a Canon "
                "with no relationships yet",
            )
        )

    if knowledge_root.is_dir():
        canon = CanonLoader().load(knowledge_root)

        if canon.load_errors:
            checks.append(
                DoctorCheck(
                    "Canon loads",
                    "error",
                    f"{len(canon.load_errors)} file(s) failed to load -- "
                    "run `forge validate` for details",
                )
            )
        else:
            checks.append(
                DoctorCheck("Canon loads", "ok", f"{len(canon)} entities")
            )

        report = CanonValidationRunner().run(knowledge_root)

        if report.success:
            checks.append(
                DoctorCheck(
                    "Canon validates",
                    "ok",
                    f"{len(report.warnings)} warning(s)",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    "Canon validates",
                    "error",
                    f"{len(report.errors)} error(s), "
                    f"{len(report.warnings)} warning(s) -- run "
                    "`forge validate` for details",
                )
            )
    else:
        checks.append(
            DoctorCheck(
                "Canon loads",
                "warning",
                "skipped -- no knowledge root to load",
            )
        )

    console.print()
    console.print(f"[bold]forge doctor[/bold] -- {target}")
    console.print()

    icon_by_status = {"ok": "[green]OK[/green]", "warning": "[yellow]WARN[/yellow]", "error": "[red]FAIL[/red]"}

    for check in checks:
        console.print(f"  [{icon_by_status[check.status]}]  {check.name}: {check.message}")

    console.print()

    error_count = sum(1 for check in checks if check.status == "error")
    warning_count = sum(1 for check in checks if check.status == "warning")

    if error_count:
        console.print(f"[bold red]{error_count} check(s) failed.[/bold red]")
        raise typer.Exit(code=1)
    elif warning_count:
        console.print(f"[bold yellow]All required checks passed[/bold yellow] ({warning_count} warning(s)).")
    else:
        console.print("[bold green]All checks passed.[/bold green]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

new_app = typer.Typer(help="Generate new knowledge artifacts.")

app.add_typer(new_app, name="new")

@new_app.command("concept")
def new_concept(
    name: str,
):
    from pathlib import Path

    from rich import print

    from numeria_forge.application.services.concept_service import (
        ConceptService,
    )

    service = ConceptService()

    files = service.create(
        Path.cwd(),
        name=name,
        canonical_id=f"concept.{name.lower()}",
        domain="mathematics",
    )

    print("[green]Created:[/green]")

    for file in files:
        print(f" • {file}")