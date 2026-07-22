# The Canonical Knowledge Model (v0.16.0)

**Codename: The Living Canon.**

> The Canon is not content -- it is a semantic, version-controlled
> knowledge graph that can be deterministically compiled into many
> educational experiences.

That's the governing idea behind this module and behind v0.14.0-0.16.0
as a whole: every book, lesson, animation, assessment, tutoring
session, game level, or future learning modality is just another
*target* of the compiler, generated from the same underlying graph.
`CanonicalKnowledgeModel` is what makes that graph queryable -- it's
the thing every future compiler target (and every future consumer
that isn't the compiler at all) reads from.

Where v0.14.0's Canon Validation Engine answers "is this Canon
structurally valid" and v0.15.0's Semantic Layer answers "does this
Canon's web of relationships form a coherent, orderable graph," the
Canonical Knowledge Model answers a third question: **how does
anything — the compiler, Numeria Studio, an AI generator — actually
*ask* the Canon a question?**

```
Canon (entities + relationships)
          |
          v
RelationshipOntology  (knowledge/ontology/relationship-types.yaml)
          |
          v
SemanticGraph          (v0.15.0 -- nodes + typed edges)
          |
          v
CanonicalKnowledgeModel  (this document)
          |
          v
KnowledgeQuery           (numeria_forge.knowledge.query)
```

Lives in `packages/numeria-forge/src/numeria_forge/knowledge/`.

## Why this isn't a new entity system

The v0.16 proposal that motivated this ("Concept, Character, Story,
Lesson, Assessment ... these are individual objects, but educational
knowledge is fundamentally a network") describes a package structure
with its own `character.py`, `concept.py`, `story.py`, `lesson.py`,
`assessment.py`, and so on under a new `knowledge/` tree. That
structure already exists — it's `numeria_forge.domain.canon`
(`CanonEntity`, `Canon`, `CanonLoader`) plus `numeria_forge.semantics`
(`SemanticGraph`, `GraphNode`, `GraphEdge`, `RelationshipOntology`,
`CycleDetector`, `topological_sort`), built across v0.14.0 and
v0.15.0. Rebuilding it as a second, parallel entity hierarchy would
mean two representations of the same Canon that could drift apart.

So `CanonicalKnowledgeModel` is not a new entity model. It's a thin
composition of the three pieces that already exist — `Canon`,
`SemanticGraph`, `RelationshipOntology` — plus the one thing that was
genuinely missing: **a stable query API** in front of them.

```python
@dataclass(frozen=True, slots=True)
class CanonicalKnowledgeModel:
    canon: Canon
    graph: SemanticGraph
    ontology: RelationshipOntology
    query: KnowledgeQuery
```

Two ways to build one:

```python
# From an already-loaded Canon + ontology (what the compiler does --
# never re-reads anything from disk):
model = CanonicalKnowledgeModel.build(canon, ontology)

# Standalone, for anything that isn't running forge compile (Numeria
# Studio, an AI generator, a notebook):
model = CanonicalKnowledgeModel.build_from_root(Path("knowledge"))
```

`build_from_root` is fail-open on a missing/malformed ontology file —
same behavior as `TopologicalOrderStage` (v0.15.0): it falls back to
an empty `RelationshipOntology` rather than raising, since
`RelationshipValidator` (part of Canon validation) already reports
that as a diagnostic elsewhere. The model still answers structural
queries (`get`, `entities_of_type`, `related`) either way; only
ontology-driven queries (`prerequisites_of`) go quiet until the
ontology is fixed.

## KnowledgeQuery: the stable surface

Everything the vision doc asks for — "traverse prerequisite, teaching,
and narrative relationships," "expose a stable query API" — lives in
`numeria_forge/knowledge/query.py`:

| Method | What it answers |
|---|---|
| `get(entity_id)` | The full entity behind an id, or `None` |
| `entities_of_type(type_name)` | Every entity of one Canon type |
| `related(entity_id, relationship_type, direction=)` | Entities directly connected by one relationship type, either direction |
| `traverse(start_id, types=, direction=, max_depth=)` | Breadth-first walk over one or more relationship types |
| `prerequisites_of(entity_id)` | Everything transitively required before this entity, nearest first |

`related()` and `traverse()` are generic — they work with *any*
relationship type declared in the ontology, not just `REQUIRES`. The
real `knowledge/ontology/relationship-types.yaml` already declares 30+
typed relationships (`REPRESENTED_BY`, `TEACHES_CONCEPT`,
`ASSESSES_CONCEPT`, `FEATURES_CHARACTER`, `APPEARS_IN`, ...), so the
"teaches," "represents," and narrative relationships the vision doc
sketches were mostly already governed by the ontology from v0.14.0 —
what was missing was a place to *ask* about them.

```python
# Which Character represents the Concept "Derivative"?
model.query.related("NUM-CON-000001", "REPRESENTED_BY")

# Which Lessons teach the Concept "Delta"? (same relationship,
# opposite direction)
model.query.related("NUM-CON-000002", "TEACHES_CONCEPT", direction="incoming")
```

`prerequisites_of` is the one convenience method built on top of the
generic primitives, because "everything needed before X" is common
enough to deserve a name. It's driven entirely by
`ontology.acyclic_type_names()` — today that's just `REQUIRES` — so it
never hardcodes a relationship type name.

### Determinism and cycle-safety

`traverse()` visits neighbors in sorted id order at each BFS level, so
its output is deterministic — consistent with Compiler Law #1
(`governance/COMPILER_LAWS.md`). It's also cycle-safe independent of
whether the relationship types involved are declared `acyclic` in the
ontology: already-visited nodes are never re-queued, so a malformed
Canon with an actual cycle in a non-acyclic relationship type still
terminates rather than hanging.

## Real example (from the actual Canon)

The real knowledge base already contains exactly the chain the vision
doc sketches:

```python
model = CanonicalKnowledgeModel.build_from_root(Path("knowledge"))
prereqs = model.query.prerequisites_of("NUM-CON-000001")  # Derivative
[(e.id, e.get("name")) for e in prereqs]
# [('NUM-CON-000006', 'Limit'),
#  ('NUM-CON-000003', 'Function'),
#  ('NUM-CON-000004', 'Variable'),
#  ('NUM-CON-000005', 'Constant')]
```

Derivative → Limit → Function → {Variable, Constant} — nearest
prerequisite first.

## What this enables, and what's deliberately not built yet

The vision doc's "structured AI context" example (a Concept + its
prerequisites + representing Characters + Realm + learning objectives
+ story constraints, assembled for an AI generator instead of a bare
prompt) is a real, worthwhile use case — but it's a *composition* of
`get`/`related`/`prerequisites_of` calls specific to one consumer's
needs, not something this module should hardcode. Baking a fixed
"AI context shape" into `KnowledgeQuery` would make the query API
speculative instead of stable. That composition belongs in whatever
calls Forge as a library (an AI generation package, Studio's backend),
built on the primitives documented above.

## Compiler pipeline integration

`BuildKnowledgeModelStage` runs after `TopologicalOrderStage`,
populating `context.knowledge_model`:

```
Load Canon -> Validate Canon -> Dependency Graph -> Topological Ordering
-> Build Knowledge Model -> Generate Missing Assets -> Publish -> ...
```

It reuses `context.loaded_canon` and `context.semantic_graph` rather
than rebuilding either — its only new work is loading the ontology
(same fail-open behavior described above). It runs unconditionally,
not gated on `context.success`: even a Canon with validation errors or
an unresolved dependency cycle still has a Canon and a graph worth
querying (diagnostics tooling, a Studio graph view that wants to
render the Canon *including* its problems).

See `docs/architecture/FORGE_COMPILER.md` for the full pipeline.

## Tests

- `tests/knowledge/test_model.py` — building from a fixture root,
  fail-open ontology handling, `build()` reusing an already-loaded
  Canon without touching disk.
- `tests/knowledge/test_query.py` — `get`, `entities_of_type`,
  `related` in both directions, `prerequisites_of` against a fixture
  Derivative→Limit→Function→{Variable,Constant} chain (mirroring the
  real Canon), `traverse` depth limiting, and cycle-safety with a
  deliberately cyclic non-acyclic relationship type.
- `tests/compiler/test_build_knowledge_model_stage.py` — stage
  ordering requirements, reuse of `context.loaded_canon` /
  `context.semantic_graph`, fail-open ontology handling.
- `tests/integration/test_knowledge_model.py` — the full lifecycle,
  driven the way `forge compile` actually runs it: a real
  `numeria.yaml` + `knowledge/` tree on disk, compiled through
  `FoundationCompiler().compile()`, then real queries
  (`entities_of_type`, `related` both directions, `prerequisites_of`,
  `traverse`, `get`) run against `result.knowledge_model.query`. Also
  covers the case a unit test can't: a Canon with a genuine dependency
  cycle still gets a populated, queryable `knowledge_model` even
  though compilation fails overall, and traversal over the cyclic
  edges terminates rather than hanging.
- Verified against the real 123-entity knowledge base: `len(canon) ==
  123`, `prerequisites_of("NUM-CON-000001")` returns the exact
  Limit → Function → Variable/Constant chain shown above, and a full
  `FoundationCompiler().compile()` run against the real repo still
  succeeds with `context.knowledge_model` populated.
