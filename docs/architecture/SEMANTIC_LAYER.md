# The Semantic Layer (v0.15.0)

Where v0.14.0's Canon Validation Engine answers "is this Canon
structurally valid" (see `CANON_MODEL.md`), the Semantic Layer answers
a different question: **does this Canon's web of relationships form a
coherent, orderable graph?** Concretely, for v0.15.0: does the
`REQUIRES` prerequisite chain between Concepts actually form a DAG, or
does it contain a cycle (Concept A requires B requires ... requires A,
which would mean nothing in the cycle can ever be the "first" thing
learned)?

```
Canon (entities + relationships)
          |
          v
RelationshipOntology  (knowledge/ontology/relationship-types.yaml,
                        typed: source/target types, symmetric, acyclic)
          |
          v
SemanticGraph  (GraphNode per entity, GraphEdge per relationship)
          |
   +------+------+
   |             |
   v             v
CycleDetector  topological_sort
   |
   v
DependencyGraphValidator  (fits the v0.14.0 CanonValidator contract)
```

Lives in `packages/numeria-forge/src/numeria_forge/semantics/`.

## RelationshipOntology

`RelationshipValidator` (v0.14.0) already reads
`knowledge/ontology/relationship-types.yaml` as a raw dict to check
source/target types on relationship entities; that code is untouched.
`semantics/ontology.py` adds a second, typed reading of the same file
for the semantics package's own needs:

```python
@dataclass(frozen=True, slots=True)
class RelationshipTypeDefinition:
    name: str
    allowed_source_types: tuple[str, ...]
    allowed_target_types: tuple[str, ...]
    symmetric: bool = False
    acyclic: bool = False
```

The new field is `acyclic`. A relationship type opts in to dependency
semantics by setting `acyclic: true` in the ontology file — not by
being hardcoded into Python. As of v0.15.0, exactly one type is marked
this way:

```yaml
REQUIRES:
  source: Concept
  target: Concept
  acyclic: true
```

`RelationshipOntology.acyclic_type_names()` returns every type name
flagged this way; that's the set `CycleDetector` and
`topological_sort` are told to check by default. Loading a missing or
malformed ontology file raises `OntologyError` — callers decide how to
handle that (see `DependencyGraphValidator` below, which fails open).

## `category` and `traversal`: one graph, several views (v0.19.0)

The original v0.15 proposal (see "What v0.15.0 does not (yet) cover"
below) sketched two semantic layers -- relationships describing
mathematics itself, versus relationships describing Numeria's
fictional universe. v0.19.0 delivers that split, but not as a second
graph engine: `RelationshipTypeDefinition` gained two more fields.

```python
@dataclass(frozen=True, slots=True)
class RelationshipTypeDefinition:
    ...
    category: str = ""     # free-form documentation: "learning", "narrative", "world", "publishing", ...
    traversal: str = ""    # which named query this type participates in: "learning", "story", ...
    ordered: bool = False  # does instance order matter (e.g. scene sequence)
    transitive: bool = False  # does A->B->C imply A->C
```

`category` is purely descriptive -- every one of the 33 real
relationship types in `knowledge/ontology/relationship-types.yaml` now
declares one, but nothing reads it except a human skimming the file.
`traversal` is the field actually consumed by code: it scopes
`RelationshipOntology.acyclic_type_names(traversal=...)`, so a query
can ask for just the acyclic types that belong to *one* named view
instead of every acyclic type combined.

```python
ontology.acyclic_type_names()                    # ("REQUIRES", "FOLLOWS_SCENE")
ontology.acyclic_type_names(traversal="learning") # ("REQUIRES",)
ontology.acyclic_type_names(traversal="story")    # ("FOLLOWS_SCENE",)
```

This exists because v0.19.0 also marked `FOLLOWS_SCENE` (Scene ->
Scene, "this scene follows that one") `acyclic: true` -- closing a
real gap: nothing previously checked a Scene sequence for cycles. With
two acyclic, order-sensitive relationship types now declared at once,
an *unscoped* query (`KnowledgeQuery.learning_path`, before this
change) would combine REQUIRES and FOLLOWS_SCENE into one meaningless
topological order over two disjoint node sets (Concepts and Scenes).
`traversal` is what keeps that from happening: `.learning_path`/
`.prerequisites_of` are scoped to `traversal="learning"`,
`.story_path` (new in v0.19.0) is scoped to `traversal="story"`. See
`CANONICAL_KNOWLEDGE_MODEL.md`'s "Views over one Canon" section for
the query-level story. `DependencyGraphValidator` (below) is
deliberately *not* scoped -- a cycle in any acyclic-declared type is a
defect regardless of which named query would have used it.

## SemanticGraph

"No graph database is needed. Just a graph model." `SemanticGraph` is
a read-only view built from a loaded `Canon`:

- One `GraphNode` (id, type) per **non-relationship** entity.
- One `GraphEdge` (id, type, source_id, target_id, description,
  metadata) per **relationship** entity, built directly from its
  `source`/`target` fields.

`SemanticGraph.build_from_canon(canon)` constructs this in one pass.
Edges whose endpoints don't resolve to an id at all are skipped, not
guessed at — a malformed relationship is `RelationshipValidator`'s
concern, not the graph's. `graph.adjacency(types=...)` builds
`{node_id: (neighbor_id, ...)}` restricted to a set of edge types (or
every type if omitted), and additionally drops any edge whose endpoint
isn't a known node (again, deferring to `RelationshipValidator` to
report dangling references).

Two v0.17.0 additions: `graph.incoming(node_id, types=)` (the mirror
of `outgoing()`, for reverse-direction queries) and
`graph.orphaned_node_ids()` (nodes touched by zero edges in either
direction -- see `CANONICAL_KNOWLEDGE_MODEL.md`). Also as of v0.17.0,
endpoint resolution accepts a second relationship schema alongside
`source`/`target`/`{id,type}`: `subject`/`object` as bare id strings
plus a `predicate` field, matching `schema: numeria.relationship.v1`.
Full detail, including the one known gap (`RelationshipValidator`
itself hasn't been extended to the new schema), is in
`CANONICAL_KNOWLEDGE_MODEL.md`.

Against the real knowledge base: 123 entities, 87 relationships ->
36 graph nodes, 87 edges, of which 7 are `REQUIRES` connecting 8
Concepts.

**Correction (found while building v0.17.0's orphan detection):** an
earlier version of this document claimed the 36 nodes were "only
entities that participate in at least one relationship." That's
wrong -- `build_from_canon` creates one `GraphNode` for *every*
non-relationship entity in the Canon, with no participation filter at
all. 36 happens to equal the *total* count of non-relationship
entities in the real Canon (123 entities - 87 relationships = 36), which
created the false impression that filtering had occurred. It hadn't.
Proof: `SemanticGraph.orphaned_node_ids()` (v0.17.0) finds 4 of those
36 nodes with zero edges in either direction -- entities that exist as
graph nodes despite participating in no relationship at all. See
`CANONICAL_KNOWLEDGE_MODEL.md`'s "Semantic integrity: orphaned
entities" section.

## CycleDetector

Classic three-color DFS (white/gray/black): a back-edge into a node
still on the current DFS stack (gray) is a cycle. `find_cycles(types=...)`
returns every cycle found as a `Cycle` (the actual node-id path, not
just true/false); `has_cycle(types=...)` is the boolean shortcut.
Recursive — fine at Numeria's current scale (low hundreds of entities);
a knowledge base large enough to hit Python's recursion limit would
need an iterative rewrite.

Real data: **zero cycles** found among the 7 `REQUIRES` edges.

## topological_sort

Kahn's algorithm: repeatedly peel off nodes with no remaining incoming
edge (restricted to the given edge types). Returns every node in the
graph, not just the ones with edges — nodes unconnected by the
requested edge types are included, ordered deterministically
(sorted by id) rather than left to dict/insertion order. If the graph
isn't a DAG, raises `TopologicalSortError(cycles)` (built using
`CycleDetector`) instead of looping forever or returning a silently
wrong partial order.

**Direction convention, worth being explicit about:** for an edge
`A -> B` (meaning "A `REQUIRES` B"), `topological_sort` places `A`
*before* `B` in the returned order, because that's the literal edge
direction. If what you actually want is a *learning* order --
prerequisites first -- reverse the result, or build the graph with
`source`/`target` swapped for that query. `topological_sort` itself
makes no assumption about which convention a given relationship type
wants; it just respects edge direction as declared.

Real data: sorts cleanly. For the 8 Concepts connected by `REQUIRES`,
`topological_sort` returns `NUM-CON-000007, NUM-CON-000008,
NUM-CON-000001, NUM-CON-000006, NUM-CON-000003, NUM-CON-000004,
NUM-CON-000005` — Derivative-family concepts before the Limit they all
ultimately require.

## DependencyGraphValidator

Fits the exact `CanonValidator` contract from v0.14.0
(`name` + `validate(context: ValidationContext) -> ValidationResult`),
so it composes with the existing engine without any interface changes.
Code: `canon.semantics.dependency-cycle`.

```python
class DependencyGraphValidator(CanonValidator):
    def validate(self, context: ValidationContext) -> ValidationResult:
        ontology = RelationshipOntology.load_from_knowledge_root(context.canon.root)
        acyclic_types = ontology.acyclic_type_names()
        graph = SemanticGraph.build_from_canon(context.canon)
        cycles = CycleDetector(graph).find_cycles(types=acyclic_types)
        # one ERROR diagnostic per cycle found
```

Two deliberate behaviors:

- If the ontology file is missing or malformed, this validator reports
  **nothing** and succeeds. `RelationshipValidator` (v0.14.0) already
  reports that as its own diagnostic; duplicating it under a second
  code would be noise for the same root cause.
- If no relationship type is marked `acyclic: true`, it also reports
  nothing — there's nothing to check.

Real data: `DependencyGraphValidator().validate(...)` against the full
123-entity Canon returns `success=True`, zero diagnostics.

### Not yet in `create_default_canon_validators()` — by design

`DependencyGraphValidator` is **not** wired into the v0.14.0 default
validator set that `forge validate` runs automatically. That default
set is a shipped contract; silently expanding what a "valid Canon"
requires (the same judgment call already made for Canon Law #1's
graduated slug enforcement) shouldn't happen without an explicit
decision to do so, even though the real Canon already passes cleanly
today.

This does **not** mean `forge compile` skips cycle detection, though:
as of this same v0.15.0 pass, `FoundationCompiler` runs
`DependencyGraphStage` and `TopologicalOrderStage` as dedicated
pipeline stages (see `FORGE_COMPILER.md`) right after Canon validation
and before package generation, independent of the validator set. A
cycle found there blocks compilation the same way a validation error
does. So there are now two independent paths to catching a dependency
cycle: `forge compile` (always, via the pipeline stages) and
`forge validate` / any other `CanonValidationRunner` call (only if
`DependencyGraphValidator` has been explicitly added to the validator
set). To include it in a `forge validate`-style run:

```python
from numeria_forge.domain.canon.validation import create_default_canon_validators
from numeria_forge.semantics import DependencyGraphValidator

validators = create_default_canon_validators() + (DependencyGraphValidator(),)
report = CanonValidationRunner(validators=validators).run(knowledge_root)
```

**Open decision:** whether/when to fold `DependencyGraphValidator` into
the default set (making "no dependency cycles" part of what `forge
validate`/`forge compile` guarantee out of the box), same shape as the
open Law #1 migration decision in `governance/CANON_LAWS.md`.

## StoryValidator (v0.19.0)

The narrative counterpart of `DependencyGraphValidator`. Same
`CanonValidator` contract, same opt-in status, same fail-open behavior
on a missing/malformed ontology. Code:
`canon.semantics.story-structure`. Also does not hardcode
`FOLLOWS_SCENE` -- it asks the ontology for whatever relationship
types are `acyclic: true` *and* `traversal: "story"`.

Where `DependencyGraphValidator` only checks for cycles,
`StoryValidator` checks a different, narrative-specific property:
every weakly-connected component of the story-traversal subgraph must
have at least one Scene with no outgoing edge of that type (a
"beginning" -- follows nothing) and at least one with no incoming edge
(an "ending" -- nothing follows it). A pure cycle with no valid
beginning/ending shows up here as two WARNING diagnostics (not an
ERROR -- `DependencyGraphValidator` is what fails the build for the
cycle itself; this validator would be redundant and noisier if it also
tried to detect the cycle).

Honestly scoped, not overclaimed: this does **not** check "every
character is reachable" or "required artifacts exist" from the
original v0.19 Story Graph sketch. Both need a first-class notion of
"which Scenes belong to this story," which the Canon doesn't have yet
-- `FOLLOWS_SCENE` today only expresses pairwise scene order, not
story membership boundaries. Deferred rather than guessed at.

## What v0.15.0 does not (yet) cover

The original v0.15 proposal sketched two "semantic layers" (roughly:
relationships that describe mathematics itself, vs. relationships that
describe the fictional universe) and a dedicated `forge` CLI surface
for the graph (e.g. a `forge graph` or `forge topo-sort` command). This
implementation delivers the concrete, testable core -- typed
relationships via the ontology, the graph model, cycle detection,
topological sort, a validator that plugs into the existing engine, and
(as of the pipeline-integration pass) `DependencyGraphStage` /
`TopologicalOrderStage` wired into `FoundationCompiler` itself -- without
yet building a standalone CLI command for the graph or formalizing the
two-layer split, since neither was specified precisely enough to
implement without guessing. Also not yet built: anything that actually
*uses* `context.topological_order` downstream (e.g. generating packages
in dependency order) -- it's computed and available on the context, but
the Generation Pipeline doesn't consume it yet. Publishing Pipeline and
Packaging Pipeline (see `FORGE_COMPILER.md`) remain unbuilt as well.

The two-layer split *was* eventually formalized -- see "`category` and
`traversal`: one graph, several views (v0.19.0)" above -- once a
concrete second layer (narrative/story) actually needed scoping
against the first (learning), rather than being speculatively built
ahead of a real second consumer. `forge graph`, a standalone CLI
command for the graph, also shipped later (v0.17.0; see
`FORGE_COMPILER.md`); a narrative equivalent (`forge story`) has not
been built as of v0.19.0.
