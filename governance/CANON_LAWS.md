# The Laws of the Canon

Where `CHARTER.md` sets out why Numeria exists, this document records the
specific, binding rules the Canon's data must obey -- the kind of rule
that should still make sense when Numeria contains 100,000+ canonical
entities.

---

## Canon Law #1 — One Identity, Three Values in Agreement

> A Canon Entity owns exactly one identity. Identity consists of:
>
> - ID
> - Slug
> - Canonical Directory
>
> Those three values must always agree.

Example:

```
ID:        NUM-CHR-000001
Slug:      detective-derivative
Directory: NUM-CHR-000001-detective-derivative
```

### Why

This keeps the Canon deterministic, consistent, and mechanically
verifiable, independent of entity type, at any scale.

### Enforcement

Enforced by two validators in
`packages/numeria-forge/src/numeria_forge/domain/canon/validation/`,
both run as part of `forge validate`, `forge compile`, and the
compiler's Validation Engine (see
`docs/architecture/CANON_MODEL.md` for the full validator list):

- `IdentityValidator` (`identity.py`, code `canon.identity`) checks that
  the ID matches the required prefix for the entity's type and flags
  duplicate display names within a type.
- `CanonLawValidator` (`canon_law.py`, code
  `canon.law-1-identity-agreement`) checks the ID/slug/directory
  agreement described above.

(`NamingValidator` in `naming.py` is kept as a deprecated alias of
`IdentityValidator` for backward compatibility; it is not a separate
validator.)

### Migration status (as of 2026-07-22)

This law is enforced as an **exact match** (`<id>-<slug>`) once an entity
has a `slug` field. Entities that don't yet have a `slug` fall back to
the older, looser "directory starts with the id" check, rather than
immediately failing validation.

This matters in practice: of the 123 entities in the current knowledge
base, only 3 had a `slug` field when this law was adopted (the
`derivative` Concept, Character, and Artifact). Making `slug` mandatory
everywhere right now would fail validation for the other ~90% of the
Canon. That's a real migration -- adding `slug` to every remaining
entity and renaming its directory to match -- not something to do
silently as a side effect of adopting this law.

Two violations were found and fixed when this law was adopted:

- `NUM-WLD-000001` (the singleton World entity, "Numeria") had no slug
  and lived at the bare `knowledge/world/` path. Now has `slug: world`
  and lives in `knowledge/world/NUM-WLD-000001-world/`.
- `NUM-CON-000001` (Concept "Derivative") declared `slug:
  detective-derivative` but its directory was still named
  `NUM-CON-000001-derivative` -- inconsistent with its own sibling
  Character (`NUM-CHR-000001-detective-derivative`), which was already
  correct. Renamed to `NUM-CON-000001-detective-derivative`.

Two stale, non-canonical leftover directories were found but
intentionally *not* touched (they contain no `entity.yaml`, so they're
invisible to validation, but they're dead clutter from earlier renames):
`knowledge/concepts/derivative/` and
`knowledge/characters/NUM-CHR-000001-derivative/`.

**Open decision:** whether to schedule the full migration (add `slug` +
rename directories for every remaining entity) now, in a batch, or leave
the graduated enforcement in place until entities are touched for other
reasons.

---

## Canon Law #2 — Directories Are Derived From Canon, Never From Filenames

> Directories are derived from Canon. Never from filenames.

Meaning: the flow is always `entity.yaml -> ID -> Slug -> Directory`,
never `Directory -> guess slug -> guess ID`.

### Enforcement

Already satisfied by design, not by a separate check: `CanonLoader`
reads `id`/`type` from each `entity.yaml`'s contents first; only after
that does `NamingValidator` compute the *expected* directory name from
that content and compare it to the actual directory. Nothing in the
Canon pipeline infers an entity's identity by parsing a path.

---

## Canon Law #3 — Nothing References Paths; Everything References IDs

> Bad: `knowledge/characters/NUM-CHR-000001...`
> Good: `NUM-CHR-000001`
>
> The compiler resolves the location. This makes refactoring safe.

### Enforcement

Satisfied by the current data and code, and now also actively checked:
relationship entities store `source`/`target` as `{id, type}`, never as
a path, `RelationshipValidator` and `SemanticValidator` resolve
everything through `Canon.entities[id]`, and `CanonEntity.source_path`
is treated purely as loader-internal bookkeeping, never as something
another entity references.

As of v0.14.0, this law also has a dedicated validator:
`IdOnlyReferenceValidator`
(`packages/numeria-forge/src/numeria_forge/domain/canon/validation/id_only_reference.py`,
code `canon.law-3-id-only-references`) walks every entity's data for any
`{id, type}`-shaped reference and flags one whose `id` value contains a
`/` or starts with `"knowledge"` -- i.e. looks like a path instead of a
bare canonical ID. The entity's own top-level `id`/`type` (its identity,
not a reference) and `source_documents` path lists are excluded, since
those are legitimately paths, not entity references.

---

## Canon Law #4 — Paths Are Implementation; IDs Are Identity

> That distinction will save us years of maintenance.

This is the principle underlying Laws #2 and #3, stated on its own
because it should guide judgment calls that aren't yet covered by an
explicit rule: when in doubt, whatever you'd need to change if a
directory got renamed is the thing that was wrong.
