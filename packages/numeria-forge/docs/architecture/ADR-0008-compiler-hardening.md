# ADR-0008: Compiler Hardening Is Additive, Not a Pass/Diagnostic Rewrite

## Status

Accepted

## Version

Numeria Forge v0.19.0

## Context

A companion proposal to the v0.19.0 Story Graph work sketched a
larger compiler restructuring: rename `CompilerStage` to
`CompilerPass`, introduce a `PassManager` that runs a registered list
of passes, replace validator exceptions with a Rust-style diagnostic
system (`Error` / `Warning` / `Information` / `Hint`, short numbered
codes like `SEM001`), evolve `CompilerContext` to a smaller
`{project, canon, ontology, diagnostics, artifacts, report,
statistics}` shape, and produce a richer end-of-compile report
(per-entity-type counts, per-format published-asset counts, duration).

Before building any of it, a gap analysis (see the conversation this
ADR originates from, and `docs/architecture/SEMANTIC_LAYER.md` /
`CANONICAL_KNOWLEDGE_MODEL.md`) checked each piece against what
already exists in `packages/numeria-forge/src/numeria_forge/compiler/`
and `domain/canon/validation/`. Most of it already exists, under
different names:

- Validators already emit diagnostics, never exceptions.
  `CanonValidator.validate()` returns a `ValidationResult` carrying a
  tuple of `Diagnostic` objects (`domain/canon/validation/result.py`).
  There has been exactly one shared `Diagnostic`/`Severity` type since
  the v0.14.0 cleanup (`numeria_forge/diagnostics.py`) -- its own
  docstring records that it replaced two separate, converging
  definitions. `CompilerContext.diagnostics` and `.success` already
  exist and already work the way the proposal describes.
- A generic, ordered-list-of-stages runner already exists:
  `numeria_forge.compiler.compiler.Compiler`. It already *is* what the
  proposal calls `PassManager` -- it just isn't named that, and until
  this ADR it was only used for the per-package sub-pipeline
  (`LoadManifestStage` / `RegisterBuiltinArtifactsStage` /
  `RenderTemplatesStage` / `PublishArtifactsStage`), not the
  foundation-wide one.
- `CompilerContext` already carries most of the proposed fields under
  slightly different names (`project_root` for `project`,
  `loaded_canon` for `canon`, `diagnostics` and `artifacts` verbatim).

What's genuinely missing: the foundation-wide pipeline in
`FoundationCompiler.compile()` is a hardcoded, linear sequence of
explicit stage calls with no way to add a stage without editing that
method. Nothing measures compile duration. The report doesn't break
down entity counts by type or published assets by format.

## Decision

Harden the compiler additively. Specifically:

- Keep `CompilerStage` as the one stage contract. No rename to
  `CompilerPass`.
- Keep the existing `Diagnostic` / `Severity` (`INFO` / `WARNING` /
  `ERROR`) system and the existing dotted diagnostic codes (e.g.
  `canon.semantics.dependency-cycle`). No short numbered code
  registry (`SEM001`, ...), no `HINT` severity added speculatively.
- Use the existing `Compiler` class as Forge's pass-runner for the
  foundation-wide pipeline too, via a new `extra_stages` parameter on
  `FoundationCompiler.__init__`, run right after
  `PublishKnowledgeGraphStage`. This is the concrete extensibility
  gap the proposal correctly identified; closing it doesn't require
  a new abstraction, only using the one that already existed for the
  per-package pipeline in a second place.
- Add `duration_seconds`, `entity_counts`, `relationship_count`, and
  `published_by_format` to `CompilationReport`, computed from data
  already on `CompilerContext` (`loaded_canon`, `published_assets`)
  plus a wall-clock timer in `FoundationCompiler.compile()`.
- Do not restructure `CompilerContext`'s field names or shape. The
  proposed `{project, canon, ontology, ...}` renaming is cosmetic
  relative to what exists (`project_root`/`loaded_canon` already mean
  the same thing) and touching every stage's field access for a
  rename is churn with no behavioral payoff.

## Rationale

A rename (`Stage` -> `Pass`, dotted codes -> numbered codes,
`project_root` -> `project`) touches every file in the pipeline for
labels that already work, without changing what the compiler actually
does. That's churn, not hardening -- it increases the diff and the
risk of the release without moving any of the five stated success
criteria (deterministic, extensible, observable, measurable,
testable). A numbered diagnostic code registry (`SEM001` meaning a
specific, permanent thing) is also a real, standing maintenance
commitment -- something has to own that registry forever, the way
rustc's error index is maintained -- which is a bigger decision than
"finish v0.19," not a smaller one.

The extensibility gap is real, though, and worth closing:
`FoundationCompiler.compile()` genuinely could not be extended from
outside `foundation_compiler.py` before this pass. Using the existing
`Compiler` class rather than inventing a `PassManager` closes that gap
with the smallest possible change -- one already-tested class, applied
to a second pipeline, rather than a second, parallel abstraction that
would need its own tests and its own reasoning about how it relates to
`Compiler`.

The report additions (duration, entity/relationship/format counts) are
purely additive fields computed from data the compiler already
collects; they change what gets *reported*, never what gets
*compiled*, so add no risk to Compiler Law #1 (determinism) or to any
existing consumer of `CompilationReport` that doesn't read the new
fields.

## Consequences

Positive:

- `FoundationCompiler` is now genuinely extensible (`extra_stages`)
  without editing its source, which is the concrete capability
  "infinitely extensible" was asking for.
- `forge compile` output is more observable and measurable (duration,
  entity/relationship/format breakdowns) without any new concepts to
  learn -- the shapes are exactly the existing `Diagnostic`/
  `CompilationReport` types, extended.
- Zero behavioral change to existing stages, validators, or diagnostic
  codes -- every diagnostic emitted before this ADR is emitted
  identically after it. Determinism (Compiler Law #1) is unaffected:
  the new report fields are computed deterministically from
  already-deterministic inputs (`loaded_canon`, `published_assets`),
  and `duration_seconds` is explicitly excluded from any
  determinism/golden-output comparison, being wall-clock by nature.

Negative:

- The `PassManager`/`CompilerPass` vocabulary from the proposal isn't
  adopted, so anyone arriving from that document won't find those
  names in the codebase -- this ADR is the pointer from that
  vocabulary to what actually exists (`Compiler`, `CompilerStage`).
- No numbered diagnostic code registry exists yet. If Forge later
  wants a stable, documented code-per-diagnostic contract (useful once
  external tooling starts pattern-matching on codes), that's still an
  open, undecided piece of work, not solved by this ADR.
- `extra_stages` only extends one specific point in the foundation-wide
  pipeline (after `PublishKnowledgeGraphStage`). A caller wanting to
  insert a stage *before* Canon validation, say, still cannot do so
  without editing `foundation_compiler.py`. Full pipeline
  reconfigurability (arbitrary insertion points) was not built --
  only the one extension point that had a concrete, current use case.

## Implementation

- `packages/numeria-forge/src/numeria_forge/compiler/foundation_compiler.py`
  -- `extra_stages` constructor parameter, run via `Compiler` after
  `PublishKnowledgeGraphStage`; wall-clock timing around the whole
  `compile()` call.
- `packages/numeria-forge/src/numeria_forge/compiler/report.py` --
  `duration_seconds`, `entity_counts`, `relationship_count`,
  `published_by_format` fields on `CompilationReport`, populated in
  `from_context`, included in `to_dict()` and
  `format_human_readable()`.

## Related Decisions

- `docs/architecture/ADR-0006-extension-framework.md` -- the existing
  hook-point extension mechanism (`HookPoint`, `PipelineStep`) for
  per-package pipelines; `extra_stages` is a second, simpler
  extension point for the foundation-wide pipeline, not a replacement
  for that framework.
- `governance/COMPILER_LAWS.md` -- Compiler Law #1 (determinism),
  which this ADR's changes are checked against and preserve.
- `docs/architecture/SEMANTIC_LAYER.md` and
  `CANONICAL_KNOWLEDGE_MODEL.md` -- the v0.19.0 "views over one
  Canon" work this hardening pass shipped alongside.
