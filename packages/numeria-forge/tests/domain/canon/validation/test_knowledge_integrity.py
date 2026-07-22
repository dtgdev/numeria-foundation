"""Tests for LoadIntegrityValidator.

As of v0.14, the old KnowledgeIntegrityValidator was split: read/parse
failures live here (LoadIntegrityValidator), duplicate IDs have their
own dedicated validator (see test_duplicate_id.py), and the CANON-status
lifecycle rule moved to SemanticValidator (see test_semantic.py). The
old class name is kept importable as a deprecated alias.
"""

from pathlib import Path

from numeria_forge.domain.canon import Canon
from numeria_forge.domain.canon.canon import CanonLoadError, CanonLoadErrorCode
from numeria_forge.domain.canon.validation import LoadIntegrityValidator, Severity
from numeria_forge.domain.canon.validation.knowledge_integrity import (
    KnowledgeIntegrityValidator,
)

from .conftest import context_for


def test_no_load_errors_passes(empty_canon: Canon) -> None:
    result = LoadIntegrityValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_read_error_is_surfaced_as_error_diagnostic(empty_canon: Canon) -> None:
    empty_canon.load_errors.append(
        CanonLoadError(
            path=Path("knowledge/x/entity.yaml"),
            message="Invalid YAML: boom",
            code=CanonLoadErrorCode.PARSE_ERROR,
        )
    )

    result = LoadIntegrityValidator().validate(context_for(empty_canon))

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.ERROR
    assert "Invalid YAML: boom" in result.diagnostics[0].message


def test_duplicate_id_errors_are_not_reported_here(empty_canon: Canon) -> None:
    # Duplicate IDs are DuplicateIdValidator's concern now, not
    # LoadIntegrityValidator's -- avoids reporting the same problem
    # twice under two different validator codes.
    empty_canon.load_errors.append(
        CanonLoadError(
            path=Path("knowledge/x/entity.yaml"),
            message="Duplicate id 'NUM-CHR-000001'; already used by y",
            code=CanonLoadErrorCode.DUPLICATE_ID,
        )
    )

    result = LoadIntegrityValidator().validate(context_for(empty_canon))

    assert result.diagnostics == ()


def test_deprecated_alias_still_importable() -> None:
    assert KnowledgeIntegrityValidator is LoadIntegrityValidator
