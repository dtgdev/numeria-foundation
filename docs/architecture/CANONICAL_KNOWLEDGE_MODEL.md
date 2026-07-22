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
| `orphaned_entities()` | Every entity touched by zero relationships in either direction (v0.17.0) |
| `learning_path(entity_id)` | The ordered sequence to learn, prerequisites first, ending with this entity (v0.18.0) |
| `story_path(scene_id)` | The ordered reading sequence of Scenes, earliest first, ending with this scene (v0.19.0) |

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

## Semantic integrity: orphaned entities (v0.17.0)

An "orphaned" entity is one no relationship touches at all -- neither
as source/subject nor target/object. Not necessarily a defect (a
brand-new Concept genuinely has no relationships until someone authors
them), but worth surfacing:

```python
model.query.orphaned_entities()
# real Canon, today: 4 entities -- one Character, one Organization,
# one Region, one World, none yet connected to anything
```

Backed by `SemanticGraph.orphaned_node_ids()`. Surfaced two ways:
always, as a count on every `forge compile` via
`CompilationReport.graph_statistics.orphaned_node_count`; optionally,
as a `WARNING` diagnostic per orphan via `OrphanedEntityValidator`
(`numeria_forge.semantics`), which is opt-in -- like
`DependencyGraphValidator` -- rather than part of the default
`forge validate` validator set, so a Canon that's still being written
doesn't get flooded with warnings for content nobody has connected
yet.

Broken references (a relationship pointing at an entity id that
doesn't exist) are *not* a new v0.17.0 check -- `RelationshipValidator`
(v0.14.0) has always reported these as `ERROR` diagnostics. Nothing
new was needed there.

## Graph export (v0.17.0)

`numeria_forge/knowledge/export.py` serializes `model.graph` to three
machine-readable formats, all built from one shared `to_dict()` so
they never drift from each other:

```python
from numeria_forge.knowledge import to_json, to_yaml, to_graphml

to_json(model)     # {"schema": "numeria.knowledge-graph.v1", "nodes": [...], "edges": [...]}
to_yaml(model)      # the same data, YAML
to_graphml(model)   # hand-written GraphML XML -- no networkx dependency
```

Deterministic: nodes sorted by id, edges sorted by `(type, id)`. These
are exactly the files `PublishKnowledgeGraphStage` writes to
`build/graph/knowledge.{json,yaml,graphml}` on every `forge compile`
(see `FORGE_COMPILER.md`).

## Graph statistics (v0.17.0)

`numeria_forge/knowledge/statistics.py`'s `GraphStatistics.from_model(model)`
computes node count, edge count, a per-relationship-type edge
breakdown, orphaned-entity count, and which relationship types the
ontology declares `acyclic`. This is what populates
`CompilationReport.graph_statistics` on every `forge compile` run --
see `FORGE_COMPILER.md`'s `CompilationReport` section.

## A second relationship schema (v0.17.0)

The real Canon's 87 relationship entities all use the v0.14.0 schema:
`source`/`target` as `{id, type}` reference objects, with the
relationship type as the entity's own top-level `type` field.
v0.17.0 introduces a second, RDF/OWL-style schema
(`schema: numeria.relationship.v1`):

```yaml
schema: numeria.relationship.v1
id: NUM-REL-000001
subject: NUM-CHR-000001
predicate: represents
object: NUM-CON-000001
status: canon
```

`subject`/`object` are bare canonical ID strings (no embedded type),
and `predicate` carries the relationship type instead of the entity's
own `type` field. `SemanticGraph.build_from_canon` accepts both
shapes -- a relationship written in either schema appears correctly
in the graph, `KnowledgeQuery`, graph exports, and graph statistics.

**Known gap:** `RelationshipValidator` (the v0.14.0 `forge validate`
check that cross-verifies each endpoint's declared type against its
actual type) has *not* been extended to the new schema -- it still
only understands `source`/`target`. A `subject`/`predicate`/`object`
relationship will build correctly into the graph but won't get that
same type-checking from `forge validate` yet. Extending it would mean
looking up each endpoint's actual type from the Canon at validation
time, since `subject`/`object` don't carry type inline the way
`source`/`target` do. Not done here because migrating or dual-writing
validation logic for a schema with zero real entities using it yet
felt premature; worth doing once the new schema sees real use.

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

## Views over one Canon (v0.19.0)

`learning_path` (v0.18.0) computes an *ordered* learning sequence, not
just the unordered `prerequisites_of` closure. v0.19.0 asked: Numeria
also has a narrative structure -- Scenes connected by `FOLLOWS_SCENE`
("this scene follows that one") -- and wants the same kind of ordered
answer for "what's the reading order up to this scene?" The original
proposal for this (see the "Story Graph" vision doc) sketched a
parallel `story/` package: `StoryNode`, `StoryEdge`, its own graph,
its own traversal, its own validator -- a second graph engine sitting
next to `SemanticGraph`.

That was deliberately not built. Instead, `story_path` is `learning_path`'s
narrative counterpart, walking the *same* `SemanticGraph` every other
query in this module uses, scoped to a different, ontology-declared
`traversal` name:

```python
def learning_path(self, entity_id: str) -> tuple[CanonEntity, ...]:
    return self._ordered_path(entity_id, traversal="learning")

def story_path(self, scene_id: str) -> tuple[CanonEntity, ...]:
    return self._ordered_path(scene_id, traversal="story")
```

Both are thin wrappers over one shared `_ordered_path` implementation
(topological sort over the ontology's `acyclic`-declared types for
that `traversal`, reversed into "earliest first," filtered to the
target's own transitive predecessors). The relationship ontology is
what tells each which edges to walk -- see `SEMANTIC_LAYER.md`'s
"`category` and `traversal`: one graph, several views" section for the
full `RelationshipTypeDefinition` schema and why `traversal` scoping
matters once more than one relationship type is `acyclic: true` at
once.

This is the "one database, many views" shape: `Canon` is the one
source of truth, `SemanticGraph` is the one graph engine, and each
named query (`learning_path`, `story_path`, and whatever comes next --
a `world_path` over `OCCURS_AT`/`LOCATED_IN`, say) is a *projection*
over it, not a new storage model. Adding a third view means adding a
`traversal` name to the ontology and a query method, not a new
package.

`StoryValidator` (`numeria_forge.semantics`, see `SEMANTIC_LAYER.md`)
is `story_path`'s validation counterpart, the narrative equivalent of
`DependencyGraphValidator`: every story-traversal component must have
a beginning and an ending. Also opt-in, also honestly scoped -- it
does not attempt "every character is reachable" or "required
artifacts exist" from the original vision doc, since both need a
first-class notion of story membership the Canon doesn't have yet.

Not built in v0.19.0: a `forge story` CLI command (the v0.17.0
`forge graph` pattern would be the template) and a `world_path`/other
additional views -- scoped out explicitly rather than spec-crept in.

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
- `tests/semantics/test_graph.py` (v0.17.0 additions) —
  `orphaned_node_ids()`, and the `subject`/`predicate`/`object` schema
  compatibility shim (both the happy path and the "incomplete, skip
  it" path).
- `tests/semantics/test_orphan_validator.py` — `OrphanedEntityValidator`
  reporting one `WARNING` per orphan, never failing validation.
- `tests/knowledge/test_export.py` — `to_json`/`to_yaml` round-trip to
  the same dict, deterministic ordering, well-formed GraphML XML
  (including one test with XML special characters in an edge type, to
  confirm escaping), and a schema/shape check against a known edge.
- `tests/knowledge/test_statistics.py` — `GraphStatistics.from_model`
  counts, the per-type edge breakdown, and `to_dict()` shape.
- `tests/compiler/test_publish_knowledge_graph_stage.py` — stage
  ordering requirements, all three files written, `PublishResult`
  accounting, overwrite-on-rerun.
- `tests/integration/test_knowledge_graph_export.py` — the full
  v0.17.0 lifecycle through the real pipeline: a fixture Canon with
  one deliberate orphan, compiled via `FoundationCompiler`, then
  `build/graph/*` files, `report.graph_statistics`, and
  `result.knowledge_model.query.orphaned_entities()` all checked
  against each other.
- Verified against the real 123-entity knowledge base: 36 graph nodes,
  87 edges, exactly 4 orphaned entities (one Character, one
  Organization, one Region, one World), and `build/graph/knowledge.json`
  / `.yaml` / `.graphml` all written correctly by a real
  `FoundationCompiler().compile()` run. Ran the real compile twice in a
  row and confirmed `report.to_json()` (including `graph_statistics`)
  is byte-identical both times -- Compiler Law #1 holds with the
  v0.17.0 stages included.
- `tests/semantics/test_ontology.py` (v0.19.0 additions) --
  `category`/`traversal`/`ordered`/`transitive` parsing,
  `acyclic_type_names(traversal=...)` scoping including the
  "no match" empty-tuple case.
- `tests/semantics/test_story_validator.py` (v0.19.0) -- a clean
  linear Scene chain passes; a 2-cycle produces exactly two WARNING
  diagnostics ("no beginning", "no ending"); two separate clean
  chains both pass independently; Scenes untouched by `FOLLOWS_SCENE`
  are correctly out of scope; fail-open on a missing ontology or on
  an ontology with no `traversal="story"` type declared.
- `tests/knowledge/test_query.py` (v0.19.0 additions) -- `story_path`
  against a fixture 3-scene chain (earliest-first, ending with the
  target; a leaf scene is just itself; an unknown id is empty), and
  two regression tests proving `.learning_path`/`.prerequisites_of`
  stay scoped to `traversal="learning"` and never cross into
  `traversal="story"` now that the fixture ontology declares both as
  acyclic at once.
- Verified against the real 123-entity knowledge base (33
  relationship types, all now `category`-annotated): `story_path` over
  the real 6-scene chain returns the exact reading order (Derivative
  Meets Delta → The Silver Delta → The Book of Change Awakens → The
  First Clue of Change → Measuring the Change → The Pattern Appears);
  `learning_path` still returns the identical Constant → Variable →
  Function → Limit → Derivative order it did before this change
  (proving the traversal-scoping refactor didn't alter v0.18.0
  behavior); `StoryValidator` against the real Canon reports zero
  diagnostics (one clean, six-scene component); and a full
  `FoundationCompiler().compile()` run against the real repo, twice in
  a row, still produces byte-identical reports -- Compiler Law #1
  holds with `FOLLOWS_SCENE` now acyclic too.
