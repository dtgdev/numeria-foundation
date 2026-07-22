# ADR-0007: Learner State Is Intentionally Excluded From Forge

## Status

Accepted

## Version

Numeria Forge v0.18.0

## Context

v0.18.0 ("Learning Graph") adds `KnowledgeQuery.learning_path()` and
`forge learn prerequisites`/`forge learn path`: the ability to
compute, from the Canon alone, the ordered sequence of Concepts
someone needs to learn before (and including) a target Concept.

The natural next questions are personal, not structural: *has this
specific learner already learned Limit? What should they do next,
given what they already know? What's their mastery level on
Derivative?* A roadmap sketch proposed `forge learn next` and `forge
learn competency` alongside `path`/`prerequisites`, plus a `mastery`
field on `LearningObjective` entities.

Building those now would require inventing a "Learner" concept --
identity, progress state, mastery scores, session history -- that
does not exist anywhere in Forge today, and deciding unprompted how
it's tracked, stored, and versioned.

## Decision

Forge will not model individual learner state -- progress, mastery,
history, or personalization -- as part of the Canon, and will not
implement `forge learn next` / `forge learn competency` (or any
command that requires knowing what a specific person has or hasn't
learned) until a Learner concept is explicitly designed.

`forge learn path` and `forge learn prerequisites` remain pure
functions of the Canon: given a target Concept, they answer "what is
the learning sequence," never "where is *this person* in it."

## Rationale

Every canonical entity already carries a required, validated
`version` field (semver, checked by `CanonRulesValidator` /
`SemanticValidator` -- see `docs/architecture/CANON_MODEL.md`) and a
lifecycle `status` (which must be `CANON` to be considered final).
That's the real, enforced sense in which the Canon is "versioned"
today. "Immutable, authored content, evolved through controlled
revisions the way source code is" is this project's stated intent for
the Canon (design intent, not yet a separately-enforced mechanism --
nothing currently stops editing a `CANON`-status entity in place), but
it's intent this decision takes seriously regardless: whether or not
immutability is mechanically enforced yet, the Canon's *purpose* is to
be one coherent, shared, authored source of truth, not a place to
record what any individual learner has done. Compiler Law #1
(`governance/COMPILER_LAWS.md`, real and enforced) builds on the same
idea: the same Canon, compiled with the same compiler version, always
produces the same output.

A learner's progress is the opposite kind of data on every axis that
matters here:

- **Mutable by nature**, not by controlled revision -- it changes
  every time the learner does anything, not through an authored
  change to canonical content.
- **Per-person, not canonical** -- "has Alice learned Limit" has as
  many answers as there are learners; it is not a fact about the
  Concept `Limit` itself, the way `REQUIRES` or `REPRESENTED_BY` are.
- **Not something `forge compile` could produce deterministically** --
  two compiles of the identical Canon would need to know about
  runtime, per-learner state to answer "what's next for this
  learner," which breaks Compiler Law #1's very premise.

Folding learner state into the Canon would mean Forge -- a
deterministic compiler over versioned content -- also becomes a
stateful, mutable, per-user system of record. That's a different kind
of system with different consistency, storage, and privacy
requirements than anything Forge does today.

## Alternatives Considered

**Add a `Learner` entity type to the Canon, with progress tracked as
relationships (e.g. `LEARNED_BY`).** Rejected for now: it would make
the Canon simultaneously "authored, versioned content" and "live,
per-user state," which is exactly the tension the previous section
argues against. Nothing about the Canon's identity/versioning/loading
model was designed with millions of small, high-frequency,
per-learner writes in mind.

**Add a `mastery` field directly on `LearningObjective` entities, as
the roadmap sketch proposed.** Rejected: `LearningObjective` is
canonical content (what a Lesson teaches), not a record of whether any
particular learner has achieved it. A field named `mastery` on the
canonical entity would conflate "the objective's own difficulty/level"
(which is legitimate canonical metadata) with "whether someone has
met it" (which is not). If a canonical difficulty/level field is
wanted, it should be named to reflect that (e.g. `difficulty_level`),
separately from this decision.

**Build `forge learn next`/`competency` against an in-memory or
file-based stub "learner," just to ship the commands.** Rejected: a
stub would either be thrown away (wasted, misleading work) or quietly
become the real design by default, without the explicit design
decision this kind of system actually needs (storage, identity,
privacy, multi-device sync are all real questions with real answers
required).

## Consequences

Positive:

- Forge's determinism guarantee (Compiler Law #1) stays airtight --
  nothing about `forge compile`'s output can ever depend on runtime
  learner state, because no such state exists inside Forge.
- The Canon stays what it's meant to be: versioned, authored content
  with one coherent identity per entity -- not a mixture of content
  and live, per-learner state.
- `forge learn path`/`prerequisites` ship now, on a solid foundation,
  instead of waiting on an unrelated, harder design problem.

Negative:

- `forge learn next` and `forge learn competency` are not available
  yet, and the roadmap's "Adaptive Tutor" (v0.19) direction depends on
  them existing somewhere -- just not inside Forge's Canon.
- Whatever eventually tracks learner state (a separate service,
  Numeria Studio, or a future Forge extension explicitly designed for
  it) will need its own identity, storage, and versioning story from
  scratch; this ADR doesn't provide one.

## Implementation

No code changes result directly from this ADR -- it documents a
boundary already respected by `commands/learn.py`'s module docstring,
which explicitly calls out that `forge learn` answers questions about
the content graph only. Any future `forge learn next`/`competency`
work, or any Learner-related Canon entity, should reference and
either extend or explicitly supersede this ADR.

## Related Decisions

- `governance/CANON_LAWS.md` (the four enforced Canon Laws --
  identity agreement, directory derivation, ID-only references, paths
  as implementation)
- `governance/COMPILER_LAWS.md` (Compiler Law #1: deterministic
  compilation)
- `docs/architecture/CANON_MODEL.md` (the `version`/`status` fields
  and the validators that enforce them)
- `docs/architecture/CANONICAL_KNOWLEDGE_MODEL.md` (the query API this
  ADR's boundary applies to)
