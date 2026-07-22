"""Single source of truth for canonical entity naming conventions.

Previously these tables were duplicated (and had drifted) across
``scripts/validate_knowledge.py`` and ``scripts/validate_naming.py``: one
had a duplicate dict key that silently dropped the ``Lesson`` prefix rule,
and the two tables disagreed with each other and were both missing
``Region`` and ``World`` (both present in the real knowledge base).
"""

from __future__ import annotations

# Non-relationship entity types, keyed to their required ID prefix.
PREFIX_BY_TYPE: dict[str, str] = {
    "Character": "NUM-CHR",
    "Artifact": "NUM-ART",
    "Location": "NUM-LOC",
    "Organization": "NUM-ORG",
    "Book": "NUM-BOOK",
    "Event": "NUM-EVT",
    "Concept": "NUM-CON",
    "LearningObjective": "NUM-LO",
    "Scene": "NUM-SCN",
    "Lesson": "NUM-LESSON",
    "Assessment": "NUM-ASMT",
    "Activity": "NUM-ACT",
    "LearningJourney": "NUM-LJ",
    "Region": "NUM-REG",
    "World": "NUM-WLD",
    # Realm: an entire world/domain of mathematical ideas (e.g. "Realm
    # of Change", "Realm of Numbers", "Realm of Geometry") that CONTAINS
    # many Regions -- Region is one level down, a geographic/spatial
    # subdivision within a Realm (e.g. "Forest of Limits", "Sigma
    # Mountains"). Canon hierarchy: Universe -> Realm -> Region ->
    # {Location, Landmark}, with Characters/Stories/Concepts also
    # belonging to a Realm. Registered on request; no Realm content
    # exists yet -- this only makes `forge validate` recognize the type
    # once someone authors one.
    "Realm": "NUM-RLM",
}

# Every relationship entity (regardless of its specific relationship
# `type`, e.g. FEATURES_CHARACTER, REQUIRES, ...) lives under this
# directory name and shares one ID prefix.
RELATIONSHIPS_DIRECTORY_NAME = "relationships"
RELATIONSHIP_PREFIX = "NUM-REL"

# Required fields per entity type, checked by EntitySchemaValidator.
# Region and World were previously undefined in the old validate_*.py
# scripts (a real coverage gap); as of v0.14 ("schema validation for all
# canon objects") they get the same baseline as every other simple entity.
REQUIRED_FIELDS_BY_TYPE: dict[str, tuple[str, ...]] = {
    "Character": ("id", "name", "type", "status", "version"),
    "Artifact": ("id", "name", "type", "status", "version"),
    "Location": ("id", "name", "type", "status", "version"),
    "Organization": ("id", "name", "type", "status", "version"),
    "Book": ("id", "title", "type", "status", "version"),
    "Event": ("id", "name", "type", "status", "version"),
    "Concept": ("id", "name", "type", "status", "version"),
    "LearningObjective": (
        "id",
        "name",
        "type",
        "status",
        "version",
        "objective",
        "grade_band",
    ),
    "Scene": ("id", "name", "type", "status", "version"),
    "Lesson": (
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "primary_concept",
        "primary_learning_objective",
    ),
    "Assessment": (
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "assessment_type",
        "learning_objective",
        "success_criteria",
    ),
    "Activity": (
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "activity_type",
        "learning_objective",
        "instructions",
    ),
    "LearningJourney": (
        "id",
        "name",
        "type",
        "status",
        "version",
        "grade_band",
        "steps",
        "primary_concept",
        "primary_learning_objective",
    ),
    "Region": ("id", "name", "type", "status", "version"),
    "World": ("id", "name", "type", "status", "version"),
    # Realm is a brand-new type with no legacy entities to migrate, so it
    # starts out requiring `slug` from day one (Canon Law #1) rather than
    # falling back to the graduated enforcement the ~90 pre-existing
    # entities still rely on.
    "Realm": ("id", "name", "type", "status", "version", "slug"),
}

# Fields required of every non-relationship entity, regardless of type.
# `EntitySchemaValidator` falls back to this for any entity type not
# listed in `REQUIRED_FIELDS_BY_TYPE` above, so schema validation covers
# every canon object rather than silently skipping unmodeled types.
BASELINE_REQUIRED_FIELDS: tuple[str, ...] = ("id", "type", "status", "version")
