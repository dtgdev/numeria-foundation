# The Forge Compiler

The Forge Compiler is the engine that turns a Numeria Foundation's raw
knowledge base into validated, generated, published, and packaged
output. This document describes what it is made of and how a
compilation actually runs, as of v0.17.0 ("Knowledge Graph").

## The pipeline, end to end

At the root of a Foundation sits `numeria.yaml`: schema version, a
`foundation` block (id, name, version), a `knowledge_root` (normally
`knowledge/`), and a list of `workspaces` (package directories the
compiler should also process). `FoundationLoader` reads this file into
a `FoundationManifest`.

`FoundationCompiler.compile(foundation_root)` is the top-level entry
point:

```
numeria.yaml
    |
    v
Project Discovery         (FoundationLoader: manifest + workspaces)
    |
    v
Load Canon                 (LoadCanonStage)
    |
    v
Validate                   (ValidateCanonStage -- ten CanonValidators:
                             schema, relationship, and semantic checks)
    |
    v
Resolve Dependencies        (DependencyGraphStage + TopologicalOrderStage,
                             v0.15.0 -- builds the graph, orders it,
                             fails the build on a dependency cycle)
    |
    v
Build Knowledge Model        (BuildKnowledgeModelStage, v0.16.0 --
                             wraps the Canon + SemanticGraph +
                             RelationshipOntology into one
                             CanonicalKnowledgeModel, queryable via
                             context.knowledge_model.query)
    |
    v
Publish Knowledge Graph      (PublishKnowledgeGraphStage, v0.17.0 --
                             exports the graph to build/graph/
                             knowledge.{json,yaml,graphml})
    |
    v
Generate Missing Assets      (GenerateMissingAssetsStage, v0.15.0 --
                             renders readme/character_card directly
                             from every Canon entity)
    |
    v
Publish                     (PublishGeneratedAssetsStage writes those
                             to build/; PublishArtifactsStage writes
                             per-package manifest output next to each
                             manifest.yaml)
    |
    v
Package                      (write_build_reports writes
                             build/reports/{compile.json,
                             diagnostics.json, diagnostics.md})
    |
    v
Compilation Report
```

"Resolve Dependencies" in the target architecture is one conceptual
step; in code it's still the two separate v0.15.0 stages
(`DependencyGraphStage` builds the graph, `TopologicalOrderStage`
orders and cycle-checks it) documented individually below and in
`SEMANTIC_LAYER.md`, since they have distinct, independently useful
outputs (`context.semantic_graph` vs. `context.topological_order`).

Concretely, `FoundationCompiler.compile` does this:

1. Load `numeria.yaml` via `FoundationLoader` into a `FoundationManifest`.
2. Build one `CompilerContext` for the whole Foundation, with
   `build_directory` set to `foundation_root / "build"`.
3. Run `LoadCanonStage` against `manifest.knowledge_root` — this loads
   every `entity.yaml` under the knowledge root into a `Canon` object
   (see `CANON_MODEL.md`) and stores it on `context.loaded_canon`.
4. Run `ValidateCanonStage` — this runs the full Canon Validation Engine
   (all ten default validators) against `context.loaded_canon` and
   appends every resulting `Diagnostic` to `context.diagnostics`.
5. Run `DependencyGraphStage` — builds `context.semantic_graph` from
   `context.loaded_canon` (see `SEMANTIC_LAYER.md`).
6. Run `TopologicalOrderStage` — computes `context.topological_order`
   over whichever relationship types the ontology marks
   `acyclic: true` (`REQUIRES`, today). A cycle here appends an
   `ERROR` diagnostic instead of raising, so it's caught by the same
   gate as validation failures.
7. Run `BuildKnowledgeModelStage` (v0.16.0) — wraps `context.loaded_canon`,
   `context.semantic_graph`, and the ontology into one
   `CanonicalKnowledgeModel` on `context.knowledge_model`, without
   rebuilding the graph or re-reading the Canon (see
   `CANONICAL_KNOWLEDGE_MODEL.md`). Runs unconditionally, like steps 5
   and 6 — a Canon with validation errors or a dependency cycle still
   has a Canon and a graph worth querying.
8. Run `PublishKnowledgeGraphStage` (v0.17.0) — exports
   `context.knowledge_model`'s graph to `build/graph/knowledge.json`,
   `knowledge.yaml`, and `knowledge.graphml`. Also unconditional, same
   reasoning as step 7.
9. If `context.success` is `False` at this point (any diagnostic is an
   `ERROR` — from validation *or* from a dependency cycle), generation
   and publishing are skipped entirely: `package_results` stays empty
   and nothing is written to `build/` except the graph export (step 8)
   and the reports (step 14 below still runs, so
   `build/reports/diagnostics.md` explains why).
   **Only a valid, acyclic Canon proceeds to generation.**
10. Otherwise: run `GenerateMissingAssetsStage` — renders `readme` (and
    `character_card` for Characters) directly from every non-relationship
    Canon entity into `context.generated_assets`.
11. Run `PublishGeneratedAssetsStage` — writes every one of those
    artifacts under `context.build_directory`, routed into
    `canon/`, `stories/`, `lessons/`, or `assessments/` by entity type
    (see "The `build/` output layout" below).
12. Walk every workspace listed in `numeria.yaml`, and for each
    `manifest.yaml` found, run a per-package `Compiler` with
    `LoadManifestStage`, `RegisterBuiltinArtifactsStage`,
    `RenderTemplatesStage`, and `PublishArtifactsStage` (writing
    output next to that `manifest.yaml`), producing its own
    `CompilerContext` per package (collected as `package_results`).
13. Build a `CompilationReport` from the foundation-wide context
    (every diagnostic accumulated across steps 4-6), including
    `graph_statistics` computed from `context.knowledge_model`
    (v0.17.0), via `CompilationReport.from_context`.
14. **Package**: call `write_build_reports(context.build_directory,
    report)`, writing `build/reports/compile.json`,
    `diagnostics.json`, and `diagnostics.md` — always, whether or not
    the build succeeded.
15. Return a `FoundationCompilationResult` wrapping the foundation-wide
    context, the report, and the tuple of package results.

Before v0.15.0, generation "legitimately compiled zero packages
against real content" because the real Canon (`entity.yaml`, IDs like
`NUM-CHR-000001`) and the manifest-driven package system (`manifest.yaml`,
IDs like `numeria:character:derivative`) were two disjoint identity
schemes, and only the latter had a generation path. `GenerateMissingAssetsStage`
closes that gap by rendering directly from Canon entities instead of
requiring every entity to also have a hand-authored manifest -- `forge
compile` against the real Foundation now reports 45 assets generated
and published (as of the current 123-entity knowledge base), still
`0 package(s) compiled` (no hand-authored `manifest.yaml` exists in the
real repo today), and `Build succeeded`.

## The stage abstraction

Every step of a compilation is a `CompilerStage`: a class with a `name`
property and an `execute(context: CompilerContext) -> CompilerContext`
method that mutates the shared context and returns it. `Compiler` is
just an ordered list of stages run against one context:

```python
class Compiler:
    def __init__(self, stages: list[CompilerStage]) -> None: ...
    def compile(self, target: CompilerContext | Path) -> CompilerContext:
        context = self._resolve_context(target)
        for stage in self._stages:
            stage.execute(context)
        return context
```

`compile()` accepts either an existing `CompilerContext` or a bare
`Path` (in which case it builds a fresh context with that path as both
`project_root` and `source_directory`). It always returns the same
mutated context it received or built — never a different object — so
callers can inspect `context.artifacts`, `context.diagnostics`, and
`context.success` afterward.

Stages shipped today: `LoadCanonStage`, `ValidateCanonStage`,
`DependencyGraphStage`, `TopologicalOrderStage`,
`BuildKnowledgeModelStage`, `PublishKnowledgeGraphStage`,
`GenerateMissingAssetsStage`, `LoadManifestStage`,
`RegisterBuiltinArtifactsStage`, `RenderTemplatesStage`,
`PublishArtifactsStage`, `PublishGeneratedAssetsStage`,
`PublishCharactersStage` (not currently wired into
`FoundationCompiler` -- nothing populates `context.characters` in that
pipeline).

## CompilerContext

`CompilerContext` is the single mutable object threaded through every
stage. The fields that matter most:

- `project_root` / `source_directory` — where this compilation is
  rooted; `source_directory` defaults to `project_root` if not given.
- `build_directory` — set by `FoundationCompiler` to
  `foundation_root / "build"`; where `PublishGeneratedAssetsStage` and
  `write_build_reports` write.
- `loaded_canon` — the `Canon` object populated by `LoadCanonStage`.
- `diagnostics: list[Diagnostic]` — every diagnostic recorded by any
  stage.
- `artifacts` — per-package, manifest-driven output
  (`RenderTemplatesStage` → `PublishArtifactsStage`).
- `generated_assets` / `published_assets` — foundation-wide,
  Canon-driven output (`GenerateMissingAssetsStage` →
  `PublishGeneratedAssetsStage`). `published_assets` holds
  `PublishResult` objects (publisher name, path, media type), the same
  type `PublishCharactersStage` already used.
- `semantic_graph` / `topological_order` (v0.15.0) — populated by
  `DependencyGraphStage` and `TopologicalOrderStage` respectively.
  Typed loosely (`Any` / a bare `tuple[str, ...]`), matching
  `loaded_canon`'s existing style, rather than importing
  `numeria_forge.semantics.SemanticGraph` into `CompilerContext`.
- `knowledge_model` (v0.16.0) — populated by `BuildKnowledgeModelStage`;
  a `CanonicalKnowledgeModel` wrapping `loaded_canon` + `semantic_graph`
  + the ontology behind one stable `query` API (see
  `CANONICAL_KNOWLEDGE_MODEL.md`). Typed loosely (`Any`), same
  reasoning as `semantic_graph` above.
- `context.success` — `True` only when no diagnostic in
  `context.diagnostics` has `Severity.ERROR`. This is the single
  source of truth a caller checks to know whether a compilation
  succeeded.

## Diagnostics

`Diagnostic` (severity, code, message, optional location) and
`Severity` (`INFO` / `WARNING` / `ERROR`) live in
`numeria_forge.diagnostics` — a neutral module with no dependency on
either the domain or compiler layers. Both the Canon Validation Engine
and the Compiler import this same type, so a diagnostic produced by a
`CanonValidator` and one produced by a compiler stage look identical
and can be reported together without translation.

## ValidateCanonStage

`ValidateCanonStage` is the compiler-side integration point for the
Canon Validation Engine (full detail in `CANON_MODEL.md`). It requires
`context.loaded_canon` to already be populated (raises `RuntimeError`
otherwise — always run `LoadCanonStage` first), wraps it in a
`ValidationContext`, runs each configured `CanonValidator` (the default
set of ten from `create_default_canon_validators()` unless overridden),
and extends `context.diagnostics` with every result's diagnostics.

## DependencyGraphStage and TopologicalOrderStage

Integrate the Semantic Layer (`numeria_forge.semantics` — full detail
in `SEMANTIC_LAYER.md`) into the compiler pipeline, running right after
`ValidateCanonStage`:

- `DependencyGraphStage` requires `context.loaded_canon` (raises
  `RuntimeError` otherwise) and builds `context.semantic_graph` — one
  node per non-relationship entity, one edge per relationship entity.
  It does not validate anything itself.
- `TopologicalOrderStage` requires `context.semantic_graph` (raises
  `RuntimeError` otherwise). It loads the ontology, restricts to
  whichever relationship types are marked `acyclic: true` (`REQUIRES`,
  today), and computes `context.topological_order`. If that subgraph
  has a cycle, it appends an `ERROR` diagnostic (code
  `canon.semantics.dependency-cycle`) to `context.diagnostics` instead
  of raising — so a dependency cycle blocks `FoundationCompiler` from
  generating output via the same `context.success` gate Canon
  validation failures use, without needing its own separate check.
  A missing or malformed ontology file is treated the same as "nothing
  to order" (empty `topological_order`, no diagnostic) rather than
  duplicating `RelationshipValidator`'s diagnostic for the same file.

This means dependency-cycle detection happens on every `forge compile`
run unconditionally — independent of whether
`DependencyGraphValidator` (the semantics package's own
`CanonValidator`) has been added to the Canon Validation Engine's
validator set. See `SEMANTIC_LAYER.md` for why that validator remains
opt-in rather than a default.

`context.topological_order` is computed but not yet consumed by
anything downstream (e.g. generating in dependency order) -- it's
available on the context for a future stage to use.

## BuildKnowledgeModelStage

Wraps `context.loaded_canon`, `context.semantic_graph`, and the
ontology into one `CanonicalKnowledgeModel` on `context.knowledge_model`
(full detail in `CANONICAL_KNOWLEDGE_MODEL.md`). Requires both
`LoadCanonStage` and `DependencyGraphStage` to have already run (raises
`RuntimeError` otherwise); reuses both rather than rebuilding the
graph or re-reading the Canon from disk. Loading the ontology is
fail-open the same way `TopologicalOrderStage` is: a missing or
malformed `ontology/relationship-types.yaml` falls back to an empty
`RelationshipOntology` rather than raising, since
`RelationshipValidator` already reports that as a diagnostic
elsewhere.

Runs unconditionally, not gated on `context.success` -- a Canon with
validation errors or an unresolved dependency cycle still has a Canon
and a graph worth querying. `context.knowledge_model.query` is the
stable API downstream consumers (the compiler itself, Numeria Studio,
AI generators) use to ask things like "everything Concept X requires"
or "which Lessons teach Concept Y" without walking `SemanticGraph` or
`Canon` directly.

## PublishKnowledgeGraphStage

Exports `context.knowledge_model`'s graph to `build/graph/`, in three
formats (`numeria_forge.knowledge.export`): `knowledge.json`,
`knowledge.yaml` (the same data, both formats built from one shared
`to_dict()`), and `knowledge.graphml` (hand-written XML, no new
dependency -- for graph-analysis tools that expect the GraphML
standard). Requires `context.knowledge_model` (raises `RuntimeError`
otherwise -- run `BuildKnowledgeModelStage` first). Runs
unconditionally, same reasoning as `BuildKnowledgeModelStage`: even an
invalid or cyclic Canon has a graph worth exporting for inspection.
All three files are deterministic (nodes sorted by id, edges sorted by
`(type, id)`) -- Compiler Law #1 holds for graph exports too, verified
by `tests/integration/test_compiler_determinism.py`.

## GenerateMissingAssetsStage

Renders default output directly from Canon entities, closing the
generation gap described above. For every entity in
`context.loaded_canon.non_relationships()`:

- Always renders the builtin `readme` artifact.
- Characters additionally get `character_card`.
- The template context is a plain dict (`{"id", "type", "title",
  "slug"}`), not the entity's raw data — `title` falls back to
  `name` then `id`, and `slug` falls back to `id`, so rendering never
  fails on Jinja2's `StrictUndefined` for the majority of the real
  Canon that predates Canon Law #1's slug requirement.
- Only the two templates that already existed
  (`domain.artifacts.create_builtin_registry`) are rendered — there is
  no Story/Lesson/Assessment-specific template yet.

Each rendered `Artifact`'s `destination` already encodes where
`PublishGeneratedAssetsStage` will write it:
`<bucket>/<type>/<id-or-id-slug>/<filename>`, where `<bucket>` is
`canon`, `stories`, `lessons`, or `assessments` (see below).

## PublishArtifactsStage

Writes `context.artifacts` to disk. Previously wrote
`artifact.destination` (a relative path like `"README.md"`) directly,
which resolved against the process's current working directory rather
than the package being compiled — effectively a no-op in practice,
since nothing exercised it. As of v0.15.0 it resolves each destination
against a base directory: an explicit `output_directory` constructor
argument, else `context.output_directory`, else
`context.source_directory`, else `context.project_root`. Defaults to
overwriting existing files (`overwrite=True`), since re-running
`forge compile` should regenerate output, not fail on a second run.

## PublishGeneratedAssetsStage

The `GenerateMissingAssetsStage` counterpart to `PublishArtifactsStage`:
writes `context.generated_assets` under `context.build_directory`
instead of a package directory, and always appends a `PublishResult`
(publisher `"publish-generated-assets"`) to `context.published_assets`.
Also always overwrites — `build/` is treated as a fully disposable,
regenerated-every-run directory, unlike hand-authored `knowledge/` or
`packages/` content.

## The `build/` output layout

```
build/
    reports/
        compile.json
        diagnostics.json
        diagnostics.md
    graph/
        knowledge.json
        knowledge.yaml
        knowledge.graphml
    canon/
        <type>/<id-or-id-slug>/README.md
        character/<id-or-id-slug>/{README.md,CHARACTER_CARD.md}
    stories/
        scene/<id>/README.md
        book/<id>/README.md
    lessons/
        lesson/<id>/README.md
    assessments/
        assessment/<id>/README.md
```

`graph/` (v0.17.0) is written by `PublishKnowledgeGraphStage` and
always present, even when the rest of generation is skipped due to a
validation failure -- see "PublishKnowledgeGraphStage" above.

Routing is by entity type
(`compiler.stages.generate_missing_assets.TYPE_DIRECTORY_BY_ENTITY_TYPE`):
`Lesson` -> `lessons/`, `Assessment` -> `assessments/`, `Scene` and
`Book` -> `stories/` (the real Canon has no literal "Story" entity
type; Scene and Book are the closest narrative-adjacent types, so
they're mapped there to match the target layout), everything else ->
`canon/`.

**No `website/` directory is produced.** The target layout sketches
one, but nothing in this codebase generates a static site --
fabricating an empty directory would misrepresent that as done.

## FoundationCompilationResult: the compiler's artifacts

`FoundationCompiler.compile()` returns one `FoundationCompilationResult`
-- the top-level, caller-facing object. It wraps `context` (the raw,
mutable `CompilerContext` every stage wrote into) and
`package_results` (one `CompilerContext` per compiled package), but
callers shouldn't need to dig into `context` for the two things a
compilation actually *produces*:

- **`.report`** — the `CompilationReport` (diagnostics, counts,
  success/failure), pre-existing since v0.14.0.
- **`.knowledge_model`** — the `CanonicalKnowledgeModel` (v0.16.0),
  built by `BuildKnowledgeModelStage`. `None` only if compilation never
  reached that stage.

Both are formally compiler *artifacts*: durable, queryable output of a
compilation, not incidental pipeline bookkeeping -- which is why each
gets its own stable property on the result instead of requiring
`result.context.report` / `result.context.knowledge_model`. A caller
who just ran `forge compile` programmatically queries the Canon this
way, with no knowledge of `CompilerContext`'s internals:

```python
result = FoundationCompiler().compile(foundation_root)

if result.success and result.knowledge_model is not None:
    prereqs = result.knowledge_model.query.prerequisites_of("NUM-CON-000001")
```

`.success`, `.artifact_count`, and `.format_report(foundation_name)`
round out the result object (see below).

## CompilationReport

`CompilationReport` summarizes one compilation: `stages_executed`,
`characters_processed`, `assets_published`, `generated_assets`, the
full `diagnostics` list, plus derived `errors` / `warnings` /
`success` properties, and (v0.17.0) `graph_statistics` --
`GraphStatistics.from_model(context.knowledge_model)`
(`numeria_forge.knowledge.statistics`): node count, edge count, a
per-relationship-type edge breakdown, orphaned-entity count, and which
relationship types the ontology declares `acyclic`. `None`, not an
all-zero `GraphStatistics`, when compilation never reached
`BuildKnowledgeModelStage` -- so a caller can tell "no graph was
built" apart from "the graph was empty." This is what satisfies
v0.17.0's "produce compilation reports that include graph statistics
and semantic validation results" success criterion, without requiring
a separate command.

- `to_json()` — a machine-readable JSON document (`success`,
  `stages_executed`, counts, `error_count`, `warning_count`,
  `graph_statistics`, and the full diagnostics list with
  severity/code/message/location) for automation and CI. This is
  exactly what `build/reports/compile.json`
  contains.
- `format_human_readable()` — a short plain-text summary plus one line
  per diagnostic, ending in `Build succeeded.` / `Build failed.`

`CompilationReport.from_context(context, stages_executed)` builds a
report by summarizing a compiled `CompilerContext`; `FoundationCompiler`
uses this to produce the report returned inside
`FoundationCompilationResult`.

## write_build_reports (Package)

`numeria_forge.compiler.build_reports.write_build_reports(build_directory,
report)` is a plain function, not a `CompilerStage` -- it needs the
final `CompilationReport`, which only exists after every stage
(including the accounting for this step itself) has run, so forcing it
into the `execute(context)` shape would mean smuggling the report
through `context` just to satisfy an interface it doesn't need.
`FoundationCompiler` calls it directly, once, right before returning.

Writes three files under `build/reports/`, always overwriting:

- `compile.json` — `report.to_dict()`, identical to `forge compile --json`.
- `diagnostics.json` — just the diagnostics slice of that same data
  (`error_count`, `warning_count`, `diagnostics`), for tooling that
  only cares about problems.
- `diagnostics.md` — the same diagnostics, formatted for humans.

Called unconditionally, even when `context.success` is `False` — a
failed build's `diagnostics.md` is exactly when it's most useful.

## The `forge compile` command

```
forge compile [path] [--json]
```

Runs the full pipeline (`FoundationCompiler().compile(target)`) against
`path` (defaulting to the current directory), then prints
`result.report.format_human_readable()` — or, with `--json`,
`result.report.to_json()`. Exits with code 1 if `result.success` is
`False`.

Unlike `forge validate`, `compile_command` does not yet have directory-
resolution smarts (`_resolve_knowledge_root`'s fallback logic): it
passes `target` straight to `FoundationCompiler().compile()`, which
requires `numeria.yaml` to exist exactly at that path. Run it from the
Foundation root, or pass the root's absolute path explicitly.

## Compiler Law #1: compilation is deterministic

`governance/COMPILER_LAWS.md` formalizes this: same Canon + same
compiler version = identical output, always -- no timestamps, random
IDs, hidden AI calls, or network dependence. Enforced by a code audit
plus `tests/integration/test_compiler_determinism.py`, which compiles
an identical fixture Canon twice (in independent directories, and
again in the same directory) and asserts the report, every generated
artifact, and every byte under `build/` are identical -- including,
as of v0.17.0, `build/graph/knowledge.{json,yaml,graphml}` and
`report.graph_statistics`, since both are covered by "every byte under
`build/`" and "the report" respectively without any test changes
required. Verified against the real knowledge base too.

## The CLI

`forge version`, `forge validate`, and `forge compile` are documented
above (or self-explanatory). Two more:

- `forge init [path] [--id] [--name]` — scaffold a new Foundation:
  `numeria.yaml` plus `knowledge/` subdirectories for every Canon
  category (characters, concepts, realms, stories, scenes, lessons,
  assessments, relationships, artifacts, ...) and a starter
  `knowledge/ontology/relationship-types.yaml`. This command already
  existed, but its original implementation predated `numeria.yaml`,
  the Canon domain model, and Canon Law #1-4 entirely -- it created
  `characters/`, `stories/`, etc. at the *repository root* and wrote a
  bespoke `.numeria` marker file, producing a tree `forge
  validate`/`forge compile` couldn't actually load. It's been rewritten
  to scaffold something those commands can load immediately (as an
  empty but internally consistent Canon), and is idempotent -- running
  it again on an already-initialized Foundation is a no-op.
- `forge doctor [path]` — a fast health-check checklist (Python
  version, `numeria.yaml`, knowledge root, ontology file presence, a
  Canon load pass, a Canon validate pass), each reported `OK`/`WARN`/
  `FAIL`. Not a replacement for `forge validate` -- it reports *that*
  the Canon fails to validate and how many errors/warnings, not the
  diagnostics themselves.

### `forge graph` (v0.17.0)

A command group (`numeria_forge/commands/graph.py`) that works
directly against `CanonicalKnowledgeModel.build_from_root` -- no
`templates/` directory or full `forge compile` pipeline required,
unlike `forge compile` itself:

```
forge graph build [path] [--json]
forge graph validate [path] [--json]
forge graph export [path] [--output DIR] [--format json|yaml|graphml|all] [--stdout]
forge graph query get ENTITY_ID [path] [--json]
forge graph query related ENTITY_ID RELATIONSHIP_TYPE [path] [--direction outgoing|incoming] [--json]
forge graph query prerequisites ENTITY_ID [path] [--json]
forge graph query traverse ENTITY_ID [path] [--types t1,t2] [--direction] [--max-depth N] [--json]
forge graph query orphans [path] [--json]
forge graph query stats [path] [--json]
```

- **`build`** — loads the Canon + ontology, builds the `SemanticGraph`,
  and checks every `acyclic`-declared relationship type for cycles
  (the same graph-building work `forge compile` does via
  `DependencyGraphStage`/`TopologicalOrderStage`/`BuildKnowledgeModelStage`,
  without also running full Canon validation or generating/publishing
  anything). Prints `GraphStatistics` and exits 1 on a cycle.
- **`validate`** — runs only the two semantics-package validators
  (`DependencyGraphValidator`, `OrphanedEntityValidator`) via
  `CanonValidationRunner` with an explicit validator set, rather than
  `forge validate`'s full ten-validator default. Since both are
  opt-in (see "What's still not built" below), this is how you check
  them without changing that default. Exits 1 only on a cycle
  (ERROR) -- orphans are WARNING and don't fail the exit code.
- **`export`** — writes `knowledge.{json,yaml,graphml}` (default:
  `<path>/build/graph/`, same as `PublishKnowledgeGraphStage`), or a
  single format to `--stdout` for piping into another tool.
- **`query`** — one subcommand per `KnowledgeQuery` method
  (`get`/`related`/`prerequisites`/`traverse`/`orphans`) plus `stats`
  (`GraphStatistics`). E.g. `forge graph query related NUM-CON-000002
  TEACHES_CONCEPT --direction incoming` answers "which Lessons teach
  this Concept" directly from the command line -- the "Query Engine"
  use case from the v0.17.0 vision doc, without needing a Python
  session.

Every subcommand accepts `--json` (or, for `export`, writes files) for
scripting; every one works against a bare `knowledge_root`, a
Foundation root with `numeria.yaml`, or a directory containing
`knowledge/`, resolved the same way as every other `forge` command
(`commands/_shared.py:resolve_knowledge_root`, factored out from
`cli.py` so both share identical path-resolution behavior).

## What's still not built

The formal `tests/integration/{test_compile_project.py,
test_validate_project.py, test_publish_character.py,
test_compiler_report.py}` suite from the v0.15.0 "Compiler Completion"
spec doesn't exist as a separately-named suite -- the tests added in
this pass live under `tests/compiler/`, `tests/test_cli.py`, and
`tests/integration/test_semantic_layer.py`, following this codebase's
existing per-stage test organization rather than introducing a new,
differently-named top-level suite. That reorganization (if still
wanted) is a natural next step.

`RelationshipValidator` (v0.14.0, schema/type-checking for
relationship entities) has not been extended to understand the
v0.17.0 `subject`/`predicate`/`object` schema
(`schema: numeria.relationship.v1`) -- only `SemanticGraph` has (see
`CANONICAL_KNOWLEDGE_MODEL.md`). A relationship entity written in that
schema will appear correctly in the graph, query API, exports, and
graph statistics, but won't get the source/target type
cross-validation `forge validate` gives the existing `source`/`target`
schema. Extending `RelationshipValidator` to the new shape (it would
need to look up each endpoint's actual type from the Canon, since
`subject`/`object` don't carry type inline) is a natural next step if
the new schema sees real use.

`OrphanedEntityValidator` (v0.17.0, `numeria_forge.semantics`) is opt-in,
like `DependencyGraphValidator` -- not part of `create_default_canon_validators()`,
so plain `forge validate` never reports orphans. Three ways to see
them anyway, in increasing order of ceremony: `forge graph query
orphans` (just the list), `forge graph validate` (the same validator,
run explicitly, WARNING diagnostics), or
`CompilationReport.graph_statistics.orphaned_node_count` (just the
count, on every `forge compile`). Add the validator to
`create_default_canon_validators()` if orphans should actually fail
plain `forge validate` too -- not done here since that's a real
behavior change to what "a valid Canon" means, same reasoning as
`DependencyGraphValidator` staying opt-in.
