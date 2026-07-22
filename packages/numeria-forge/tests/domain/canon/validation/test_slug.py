"""Tests for the retired SlugValidator.

Renamed `DuplicateSlugValidator` for exact terminology match with the
v0.14.0 Core Validators list -- see test_duplicate_slug.py. The old name
is kept importable as a deprecated alias.
"""

from numeria_forge.domain.canon.validation import DuplicateSlugValidator
from numeria_forge.domain.canon.validation.slug import SlugValidator


def test_deprecated_alias_still_importable() -> None:
    assert SlugValidator is DuplicateSlugValidator
