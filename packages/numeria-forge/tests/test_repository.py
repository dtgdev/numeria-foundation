from pathlib import Path

import pytest

from numeria_forge.infrastructure.repository import RepositoryWriter


def test_writer_creates_file(tmp_path: Path):
    writer = RepositoryWriter()

    destination = tmp_path / "hello.txt"

    writer.write(destination, "Hello Forge")

    assert destination.exists()
    assert destination.read_text() == "Hello Forge"


def test_writer_refuses_overwrite(tmp_path: Path):
    writer = RepositoryWriter()

    destination = tmp_path / "hello.txt"

    writer.write(destination, "Version 1")

    with pytest.raises(FileExistsError):
        writer.write(destination, "Version 2")


def test_writer_overwrite_allowed(tmp_path: Path):
    writer = RepositoryWriter()

    destination = tmp_path / "hello.txt"

    writer.write(destination, "Version 1")

    writer.write(
        destination,
        "Version 2",
        overwrite=True,
    )

    assert destination.read_text() == "Version 2"
