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
    assert "doctor" in result.stdout


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "Numeria Forge 0.1.0" in result.stdout


def test_init_command(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert "Numeria Foundation initialized." in result.stdout

    expected_directories = [
        "knowledge/characters",
        "knowledge/concepts",
        "knowledge/realms",
        "knowledge/stories",
        "knowledge/scenes",
        "knowledge/lessons",
        "knowledge/assessments",
        "knowledge/relationships",
        "knowledge/artifacts",
        "knowledge/ontology",
    ]

    for relative_directory in expected_directories:
        assert (tmp_path / relative_directory).is_dir()

    assert (tmp_path / "numeria.yaml").is_file()
    assert (tmp_path / "knowledge" / "ontology" / "relationship-types.yaml").is_file()


def test_init_command_is_idempotent(tmp_path: Path) -> None:
    first = runner.invoke(app, ["init", str(tmp_path)])
    assert first.exit_code == 0

    second = runner.invoke(app, ["init", str(tmp_path)])
    assert second.exit_code == 0
    assert "Nothing to do" in second.stdout


def test_init_then_validate_succeeds_on_an_empty_canon(tmp_path: Path) -> None:
    init_result = runner.invoke(app, ["init", str(tmp_path)])
    assert init_result.exit_code == 0

    validate_result = runner.invoke(app, ["validate", str(tmp_path)])
    assert validate_result.exit_code == 0
    assert "internally consistent" in validate_result.stdout


def test_doctor_on_an_uninitialized_directory_reports_missing_manifest(
    tmp_path: Path,
) -> None:
    result = runner.invoke(app, ["doctor", str(tmp_path)])

    assert "numeria.yaml" in result.stdout
    assert "not found" in result.stdout


def test_doctor_after_init_reports_a_clean_canon(tmp_path: Path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(app, ["doctor", str(tmp_path)])

    assert "Canon loads: 0 entities" in result.stdout
    assert "Canon validates: 0 warning(s)" in result.stdout
