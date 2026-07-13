ADR-0001: Semantic Core as the Canonical Source of Truth

Status: Accepted
Date: July 13, 2026
Decision Owners: Numeria Foundation
Project: Project Atlas

Context

Numeria will produce many representations of mathematical knowledge, including:

* Characters
* Stories
* Books
* Lessons
* Worksheets
* Games
* Animation
* Assessments
* AI tutor conversations
* Teacher resources

Without a shared source of truth, mathematical definitions and educational explanations could be duplicated across these experiences.

Over time, duplicated knowledge could become inconsistent, outdated, or mathematically incorrect.

Numeria requires an architecture that supports many creative and educational experiences while preserving one coherent representation of the underlying knowledge.

Decision

Numeria will establish a Semantic Core as the canonical structured source of truth for mathematical knowledge and its relationships.

Books, characters, stories, lessons, games, animation, curriculum, and AI systems will reference the Semantic Core rather than independently redefining canonical mathematical concepts.

The Semantic Core will include:

* Canonical entities
* Stable identifiers
* Explicit relationships
* Version information
* Lifecycle status
* Provenance
* Educational mappings
* Narrative mappings
* Media mappings

Rationale

This decision supports the principle:

Author knowledge once. Experience it everywhere.

A mathematical concept such as the derivative should have one canonical semantic identity.

Different experiences may explain or dramatize that concept in different ways, but they must remain connected to the same underlying knowledge entity.

This architecture provides:

* Mathematical consistency
* Reduced duplication
* Traceability
* Reusability
* Easier maintenance
* Strong grounding for AI
* Support for multiple learning levels
* Support for multiple languages and media

Example

NUM-CON-000001
Derivative
   │
   ├── representedBy → NUM-CHR-000001
   ├── taughtIn → NUM-LES-000001
   ├── appearsIn → NUM-STO-000001
   ├── assessedBy → NUM-ASM-000001
   └── adaptedAs → NUM-MED-000001

The derivative concept is defined once.

Detective Derivative, Book One, lessons, assessments, animations, and AI tutor experiences reference that concept.

Alternatives Considered

Store definitions separately in every product

Rejected because definitions would be duplicated and could drift apart.

Treat stories as the primary source of knowledge

Rejected because narrative representations may simplify ideas and should not replace canonical mathematical truth.

Use only unstructured Markdown documents

Rejected as the sole architecture because unstructured documents are difficult for validation, graph traversal, automation, and AI grounding.

Markdown may still provide human-readable mathematical references.

Build the knowledge graph later

Rejected because adding semantic structure after producing large amounts of content would require expensive restructuring and reconciliation.

Consequences

Positive

* Mathematical truth remains consistent.
* Experiences can be generated from shared knowledge.
* AI systems can be grounded in approved entities.
* Concepts can be reused across age levels and media.
* Changes remain traceable.
* Relationships can be queried and validated.

Tradeoffs

* Contributors must learn the distinction between knowledge and experience.
* Canonical entities require structured metadata.
* Validation and governance processes must be maintained.
* Initial content creation may require more discipline.

Implementation

The Semantic Core will be represented initially through version-controlled YAML files located under:

ontology/
schemas/
knowledge/

Responsibilities are separated as follows:

* ontology/ defines what entity and relationship types may exist.
* schemas/ defines validation rules.
* knowledge/ contains canonical entity instances.

Future graph databases, APIs, or AI services may consume these files without changing the core architectural principle.

Related Principles

* Mathematics is the source of truth.
* Stories reveal mathematics; they do not replace it.
* Every canonical entity has a permanent identity.
* Every important change is versioned and traceable.
* Knowledge is the product; experiences are expressions of knowledge.

Decision Outcome

The Semantic Core is established as the canonical structured knowledge foundation for Numeria.

All future educational and creative experiences should reference it.