from pathlib import Path

import pytest

from numeria_forge.infrastructure.foundation_loader import FoundationLoader


def test_loads_numeria_yaml(tmp_path: Path) -> None:
    (tmp_path / "numeria.yaml").write_text(
        """
schema_version: "1.0"

foundation:
  id: numeria-foundation
  name: Numeria Foundation
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
  - packages/numeria-forge
""".strip(),
        encoding="utf-8",
    )

    manifest = FoundationLoader().load(tmp_path)

    assert manifest.metadata.id == "numeria-foundation"
    assert manifest.metadata.name == "Numeria Foundation"
    assert manifest.knowledge_root == tmp_path / "knowledge"
    assert manifest.workspaces == (tmp_path / "packages/numeria-forge",)


def test_missing_manifest_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        FoundationLoader().load(tmp_path)


def test_missing_foundation_section_raises(tmp_path: Path) -> None:
    (tmp_path / "numeria.yaml").write_text(
        "schema_version: \"1.0\"\n", encoding="utf-8"
    )

    with pytest.raises(ValueError):
        FoundationLoader().load(tmp_path)
