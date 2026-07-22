"""Typed model of `knowledge/ontology/relationship-types.yaml`.

`RelationshipValidator` (see `domain.canon.validation.relationships`)
reads this same file as a raw dict and stays untouched here for
backward compatibility. The semantics package needs more than "what
source/target types does this relationship type allow" -- it needs to
know which relationship types describe a strict dependency order (e.g.
a Concept `REQUIRES` another Concept as a prerequisite) so cycle
detection and topological sort know which edges to consider. That is
the `acyclic` flag below: an ontology-declared property, not a
hardcoded Python set, so a future relationship type can opt in to
dependency semantics just by editing YAML.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_ONTOLOGY_PATH_SEGMENTS = ("ontology", "relationship-types.yaml")


class OntologyError(ValueError):
    """Raised when the ontology file is missing, unreadable, or malformed."""


def _as_tuple(value: object) -> tuple[str, ...]:
    if not value:
        return ()

    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)

    return (str(value),)


@dataclass(frozen=True, slots=True)
class RelationshipTypeDefinition:
    """One entry under `relationship_types:` in the ontology file.

    `category` and `traversal` (v0.19.0 -- "Views over One Canon") are
    descriptive grouping fields, not consumed by `allows()` or by
    graph-building: `category` is free-form documentation of what kind
    of relationship this is (`learning`, `narrative`, `world`,
    `publishing`, ...), while `traversal` names the specific query a
    relationship type participates in (`learning`, `story`, ...) and
    is what `RelationshipOntology.acyclic_type_names(traversal=...)`
    filters on. Multiple relationship types can share a `category`
    without sharing a `traversal` -- `traversal` is the narrower,
    query-scoping field.

    `ordered` and `transitive` are likewise descriptive metadata about
    the relationship's shape (does instance order matter, e.g. scene
    sequence; does A->B->C imply A->C). Neither is consumed by any
    validator or traversal today -- they exist so relationship types
    can declare their own semantics in one place rather than every
    consumer re-deciding it, the same way `acyclic` started as
    descriptive metadata before `DependencyGraphValidator` and
    `topological_sort` were built to consume it.
    """

    name: str
    allowed_source_types: tuple[str, ...]
    allowed_target_types: tuple[str, ...]
    symmetric: bool = False
    acyclic: bool = False
    category: str = ""
    traversal: str = ""
    ordered: bool = False
    transitive: bool = False

    def allows(self, source_type: str, target_type: str) -> bool:
        return (
            source_type in self.allowed_source_types
            and target_type in self.allowed_target_types
        )


@dataclass(frozen=True, slots=True)
class RelationshipOntology:
    """The full set of declared relationship types for one knowledge root."""

    path: Path
    version: str
    status: str
    types: dict[str, RelationshipTypeDefinition] = field(default_factory=dict)

    def __contains__(self, type_name: str) -> bool:
        return type_name in self.types

    def __iter__(self):
        return iter(self.types.values())

    def get(self, type_name: str) -> RelationshipTypeDefinition | None:
        return self.types.get(type_name)

    def acyclic_type_names(self, *, traversal: str | None = None) -> tuple[str, ...]:
        """Relationship types that must never form a cycle (e.g. REQUIRES).

        With no `traversal` filter (the default), this returns every
        acyclic-declared type combined -- what
        `DependencyGraphValidator` wants, since a cycle in *any*
        acyclic-declared relationship type is a defect regardless of
        which query uses it.

        Pass `traversal=` (v0.19.0) to scope to one named query
        instead, e.g. `traversal="learning"` for just `REQUIRES` or
        `traversal="story"` for just `FOLLOWS_SCENE` -- what
        `KnowledgeQuery.learning_path`/`.story_path` want, so that
        having two (or more) acyclic relationship types declared at
        once never mixes unrelated graphs into one topological order.
        """

        return tuple(
            name
            for name, definition in self.types.items()
            if definition.acyclic
            and (traversal is None or definition.traversal == traversal)
        )

    @classmethod
    def load(cls, path: Path) -> "RelationshipOntology":
        if not path.is_file():
            raise OntologyError(f"Ontology file not found: {path}")

        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise OntologyError(f"Invalid YAML in {path}: {exc}") from exc

        if not isinstance(raw, dict):
            raise OntologyError(f"Ontology root must be a mapping: {path}")

        raw_types = raw.get("relationship_types") or {}

        if not isinstance(raw_types, dict):
            raise OntologyError(
                f"'relationship_types' must be a mapping in {path}"
            )

        types: dict[str, RelationshipTypeDefinition] = {}

        for type_name, rule in raw_types.items():
            rule = rule or {}

            types[type_name] = RelationshipTypeDefinition(
                name=type_name,
                allowed_source_types=_as_tuple(rule.get("source")),
                allowed_target_types=_as_tuple(rule.get("target")),
                symmetric=bool(rule.get("symmetric", False)),
                acyclic=bool(rule.get("acyclic", False)),
                category=str(rule.get("category", "")),
                traversal=str(rule.get("traversal", "")),
                ordered=bool(rule.get("ordered", False)),
                transitive=bool(rule.get("transitive", False)),
            )

        return cls(
            path=path,
            version=str(raw.get("version", "")),
            status=str(raw.get("status", "")),
            types=types,
        )

    @classmethod
    def load_from_knowledge_root(cls, knowledge_root: Path) -> "RelationshipOntology":
        return cls.load(knowledge_root.joinpath(*DEFAULT_ONTOLOGY_PATH_SEGMENTS))
