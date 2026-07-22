"""Factory for the standard set of canon validators."""

from __future__ import annotations

from numeria_forge.domain.canon.validation.base import CanonValidator

from .canon_law import CanonLawValidator
from .canon_rules import CanonRulesValidator
from .duplicate_id import DuplicateIdValidator
from .duplicate_slug import DuplicateSlugValidator
from .entity_schema import EntitySchemaValidator
from .id_only_reference import IdOnlyReferenceValidator
from .identity import IdentityValidator
from .load_integrity import LoadIntegrityValidator
from .relationships import RelationshipValidator
from .semantic import SemanticValidator


def create_default_canon_validators() -> tuple[CanonValidator, ...]:
    """Create the standard set of canon validators shipped with Forge,
    roughly in pipeline order: load integrity, identity (duplicate ID,
    schema, ID format, Canon Law #1, duplicate slug), references (Canon
    Law #3, cross-reference), then business rules and semantics.
    """

    return (
        LoadIntegrityValidator(),
        DuplicateIdValidator(),
        EntitySchemaValidator(),
        IdentityValidator(),
        CanonLawValidator(),
        DuplicateSlugValidator(),
        IdOnlyReferenceValidator(),
        RelationshipValidator(),
        CanonRulesValidator(),
        SemanticValidator(),
    )
