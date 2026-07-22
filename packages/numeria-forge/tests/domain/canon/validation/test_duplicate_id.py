from pathlib import Path

from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.canon import CanonLoadError, CanonLoadErrorCode
from numeria_forge.domain.canon.validation import DuplicateIdValidator, Severity

from .conftest import context_for


def test_no_duplicates_passes(empty_canon: Canon) -> None:
    result = DuplicateIdValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_duplicate_id_load_error_is_surfaced(empty_canon: Canon) -> None:
    empty_canon.load_errors.append(
        CanonLoadError(
            path=Path("knowledge/characters/dup/entity.yaml"),
            message="Duplicate id 'NUM-CHR-000001'; already used by x",
            code=CanonLoadErrorCode.DUPLICATE_ID,
        )
    )

    result = DuplicateIdValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.ERROR
    assert "Duplicate id" in result.diagnostics[0].message


def test_non_duplicate_load_errors_are_ignored(empty_canon: Canon) -> None:
    empty_canon.load_errors.append(
        CanonLoadError(
            path=Path("knowledge/characters/broken/entity.yaml"),
            message="Invalid YAML: boom",
            code=CanonLoadErrorCode.PARSE_ERROR,
        )
    )

    result = DuplicateIdValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()
