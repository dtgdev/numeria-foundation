"""Tests for the retired NamingValidator.

As of the v0.14.0 Canonical Validator Framework cleanup,
`NamingValidator` was split into `IdentityValidator` (ID format,
duplicate display names -- see test_identity.py) and `CanonLawValidator`
(Canon Law #1: id/slug/directory agreement -- see test_canon_law.py).
The old name is kept importable as a deprecated alias for
`IdentityValidator`.
"""

from numeria_forge.domain.canon.validation import IdentityValidator
from numeria_forge.domain.canon.validation.naming import NamingValidator


def test_deprecated_alias_still_importable() -> None:
    assert NamingValidator is IdentityValidator
