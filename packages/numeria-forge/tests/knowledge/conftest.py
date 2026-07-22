"""Fixture Canon for the Canonical Knowledge Model (v0.16.0) tests.

Mirrors the real repo's Derivative -> Limit -> Function -> {Variable,
Constant} REQUIRES chain (see docs/architecture/CANONICAL_KNOWLEDGE_MODEL.md),
plus one TEACHES_CONCEPT edge and one REPRESENTED_BY edge, so tests
exercise `related()` in both directions without needing the real
knowledge base. Also includes a small 3-scene FOLLOWS_SCENE chain
(v0.19.0 -- "Views over One Canon"), mirroring the real repo's Scene
sequence, so `.story_path` can be tested the same way `.learning_path`
is tested against the REQUIRES chain, and so both acyclic,
traversal-scoped relationship types (`REQUIRES` traversal="learning",
`FOLLOWS_SCENE` traversal="story") are present at once -- proving
`.learning_path`/`.story_path` stay scoped to their own traversal
rather than combining into one topological order.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from numeria_forge.knowledge import CanonicalKnowledgeModel


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _write_relationship(
    directory: Path,
    *,
    rel_id: str,
    rel_type: str,
    source_id: str,
    source_type: str,
    target_id: str,
    target_type: str,
) -> None:
    _write_entity(
        directory,
        id=rel_id,
        type=rel_type,
        status="CANON",
        version="1.0.0",
        source={"id": source_id, "type": source_type},
        target={"id": target_id, "type": target_type},
    )


def knowledge_root(tmp_path: Path) -> Path:
    root = tmp_path / "knowledge"

    _write_entity(
        root / "concepts" / "variable",
        id="CON-VARIABLE", type="Concept", status="CANON", version="1.0.0",
        name="Variable",
    )
    _write_entity(
        root / "concepts" / "constant",
        id="CON-CONSTANT", type="Concept", status="CANON", version="1.0.0",
        name="Constant",
    )
    _write_entity(
        root / "concepts" / "function",
        id="CON-FUNCTION", type="Concept", status="CANON", version="1.0.0",
        name="Function",
    )
    _write_entity(
        root / "concepts" / "limit",
        id="CON-LIMIT", type="Concept", status="CANON", version="1.0.0",
        name="Limit",
    )
    _write_entity(
        root / "concepts" / "derivative",
        id="CON-DERIVATIVE", type="Concept", status="CANON", version="1.0.0",
        name="Derivative",
    )
    _write_entity(
        root / "characters" / "detective-derivative",
        id="CHR-DETECTIVE", type="Character", status="CANON", version="1.0.0",
        name="Detective Derivative",
    )
    _write_entity(
        root / "lessons" / "intro",
        id="LESSON-INTRO", type="Lesson", status="CANON", version="1.0.0",
        name="Intro to Derivatives",
    )
    _write_entity(
        root / "scenes" / "opening",
        id="SCN-OPENING", type="Scene", status="CANON", version="1.0.0",
        name="Opening",
    )
    _write_entity(
        root / "scenes" / "middle",
        id="SCN-MIDDLE", type="Scene", status="CANON", version="1.0.0",
        name="Middle",
    )
    _write_entity(
        root / "scenes" / "climax",
        id="SCN-CLIMAX", type="Scene", status="CANON", version="1.0.0",
        name="Climax",
    )

    _write_relationship(
        root / "relationships" / "function-requires-variable",
        rel_id="REL-001", rel_type="REQUIRES",
        source_id="CON-FUNCTION", source_type="Concept",
        target_id="CON-VARIABLE", target_type="Concept",
    )
    _write_relationship(
        root / "relationships" / "function-requires-constant",
        rel_id="REL-002", rel_type="REQUIRES",
        source_id="CON-FUNCTION", source_type="Concept",
        target_id="CON-CONSTANT", target_type="Concept",
    )
    _write_relationship(
        root / "relationships" / "limit-requires-function",
        rel_id="REL-003", rel_type="REQUIRES",
        source_id="CON-LIMIT", source_type="Concept",
        target_id="CON-FUNCTION", target_type="Concept",
    )
    _write_relationship(
        root / "relationships" / "derivative-requires-limit",
        rel_id="REL-004", rel_type="REQUIRES",
        source_id="CON-DERIVATIVE", source_type="Concept",
        target_id="CON-LIMIT", target_type="Concept",
    )
    _write_relationship(
        root / "relationships" / "derivative-represented-by",
        rel_id="REL-005", rel_type="REPRESENTED_BY",
        source_id="CON-DERIVATIVE", source_type="Concept",
        target_id="CHR-DETECTIVE", target_type="Character",
    )
    _write_relationship(
        root / "relationships" / "lesson-teaches-derivative",
        rel_id="REL-006", rel_type="TEACHES_CONCEPT",
        source_id="LESSON-INTRO", source_type="Lesson",
        target_id="CON-DERIVATIVE", target_type="Concept",
    )
    _write_relationship(
        root / "relationships" / "middle-follows-opening",
        rel_id="REL-007", rel_type="FOLLOWS_SCENE",
        source_id="SCN-MIDDLE", source_type="Scene",
        target_id="SCN-OPENING", target_type="Scene",
    )
    _write_relationship(
        root / "relationships" / "climax-follows-middle",
        rel_id="REL-008", rel_type="FOLLOWS_SCENE",
        source_id="SCN-CLIMAX", source_type="Scene",
        target_id="SCN-MIDDLE", target_type="Scene",
    )

    ontology_dir = root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        """
version: "1.0.0"
status: CANON

relationship_types:
  REQUIRES:
    source: Concept
    target: Concept
    acyclic: true
    category: learning
    traversal: learning
  REPRESENTED_BY:
    source: Concept
    target: Character
  TEACHES_CONCEPT:
    source: Lesson
    target: Concept
  FOLLOWS_SCENE:
    source: Scene
    target: Scene
    acyclic: true
    category: narrative
    traversal: story
    ordered: true
""".strip(),
        encoding="utf-8",
    )

    return root


def model(tmp_path: Path) -> CanonicalKnowledgeModel:
    return CanonicalKnowledgeModel.build_from_root(knowledge_root(tmp_path))
