from pathlib import Path

import pytest

from numeria_forge.domain.canon import Canon, CanonEntity
from numeria_forge.domain.canon.validation import ValidationContext


def make_entity(entity_id: str, entity_type: str, path: str, **data) -> CanonEntity:
    return CanonEntity(
        id=entity_id,
        type=entity_type,
        source_path=Path(path),
        data=data,
    )


@pytest.fixture
def empty_canon(tmp_path: Path) -> Canon:
    return Canon(root=tmp_path)


def context_for(canon: Canon) -> ValidationContext:
    return ValidationContext(canon=canon)
