from pathlib import Path

from typer.testing import CliRunner

from numeria_forge.cli import app


runner = CliRunner()


def test_help_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Forge mathematical worlds from canonical knowledge." in result.stdout
    assert "version" in result.stdout
    assert "init" in result.stdout


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "Numeria Forge 0.1.0" in result.stdout


def test_init_command(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert "Numeria repository is ready." in result.stdout

    expected_directories = [
        "docs/foundation",
        "knowledge/concepts",
        "knowledge/graph",
        "characters",
        "stories",
        "lessons",
        "assessments",
        "animation",
        "short-videos",
    ]

    for relative_directory in expected_directories:
        assert (tmp_path / relative_directory).is_dir()

    marker = tmp_path / ".numeria"

    assert marker.is_file()
