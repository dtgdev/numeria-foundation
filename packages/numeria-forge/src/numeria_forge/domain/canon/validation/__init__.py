from numeria_forge.diagnostics import Diagnostic, Severity

from .base import CanonValidator
from .canon_law import CanonLawValidator
from .canon_rules import CanonRulesValidator
from .context import ValidationContext
from .duplicate_id import DuplicateIdValidator
from .duplicate_slug import DuplicateSlugValidator
from .entity_schema import EntitySchemaValidator
from .id_only_reference import IdOnlyReferenceValidator
from .identity import IdentityValidator
from .load_integrity import LoadIntegrityValidator
from .registry import create_default_canon_validators
from .relationships import RelationshipValidator
from .report import CanonValidationReport
from .result import ValidationResult
from .runner import CanonValidationRunner
from .semantic import SemanticValidator

# Backward-compatible aliases for names used before the v0.14.0
# Canonical Validator Framework cleanup.
CanonDiagnostic = Diagnostic
CanonSeverity = Severity

__all__ = [
    "CanonDiagnostic",
    "CanonLawValidator",
    "CanonRulesValidator",
    "CanonSeverity",
    "CanonValidationReport",
    "CanonValidationRunner",
    "CanonValidator",
    "Diagnostic",
    "DuplicateIdValidator",
    "DuplicateSlugValidator",
    "EntitySchemaValidator",
    "IdOnlyReferenceValidator",
    "IdentityValidator",
    "LoadIntegrityValidator",
    "RelationshipValidator",
    "SemanticValidator",
    "Severity",
    "ValidationContext",
    "ValidationResult",
    "create_default_canon_validators",
]
