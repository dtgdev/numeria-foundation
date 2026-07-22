# The Canon Model

The Canon is the Numeria Foundation's knowledge base: every character,
concept, location, scene, and relationship that has been declared
canonical, each expressed as one `entity.yaml` file somewhere under
`knowledge/`. This document describes the domain model that represents
a loaded Canon and the Validation Engine that checks it. For how the
Compiler wires these into a full build, see `FORGE_COMPILER.md`.

As of v0.14.0, Forge can answer the question its Validation Engine was
built to answer: **is this Canon internally consistent?** Only a valid
Canon proceeds to compilation.

## Canon, CanonEntity, CanonLoader

`Canon` is the full set of entities loaded from one knowledge root:

```python
@dataclass(slots=True)
class Canon:
    root: Path
    entities: dict[str, CanonEntity]
    load_errors: list[CanonLoadError]

    def by_type(self, entity_type: str) -> tuple[CanonEntity, ...]: ...
    def relationships(self) -> tuple[CanonEntity, ...]: ...
    def non_relationships(self) -> tuple[CanonEntity, ...]: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[CanonEntity]: ...
    def __contains__(self, entity_id: object) -> bool: ...
```

`CanonEntity` is a deliberately permissive, loosely-typed wrapper around
one parsed `entity.yaml` (`id`, `type`, `source_path`, and the raw
`data` mapping) — unlike `Character` (see below), it does not enforce a
fixed schema, because the real knowledge base has many entity types
with very different shapes; validators decide what each type requires.
`entity.is_relationship` is `True` when `"relationships"` appears
anywhere in `source_path.parts`.

`CanonLoader.load(knowledge_root)` walks every `entity.yaml` under a
knowledge root and builds a `Canon`. Its defining property, compared to
the original `scripts/validate_*.py` scripts it replaced: **a single
bad file never aborts the load or crashes with a raw traceback.** Every
problem — a missing root, an unreadable file, invalid YAML, a
non-mapping root, a missing `id`/`type`, a duplicate `id` — is recorded
as a `CanonLoadError` on the returned `Canon` and loading continues.
Each `CanonLoadError` carries a `CanonLoadErrorCode` (`MISSING_ROOT`,
`READ_ERROR`, `PARSE_ERROR`, `INVALID_SHAPE`, `MISSING_ID`,
`MISSING_TYPE`, `DUPLICATE_ID`) so validators can filter by kind of
problem instead of pattern-matching message strings — this is how
`DuplicateIdValidator` and `LoadIntegrityValidator` (see below) can each
own a distinct, non-overlapping slice of the same `load_errors` list.

## Naming conventions: `prefixes.py`

`packages/numeria-forge/src/numeria_forge/domain/canon/prefixes.py` is
the single source of truth for entity naming, replacing two tables that
had previously drifted independently in
`scripts/validate_knowledge.py` and `scripts/validate_naming.py` (one
had a duplicate dict key that silently dropped the `Lesson` prefix
rule; both disagreed with each other and were both missing `Region` and
`World`).

- `PREFIX_BY_TYPE` — required ID prefix per entity type (`Character` ->
  `NUM-CHR`, `Concept` -> `NUM-CON`, `World` -> `NUM-WLD`, `Realm` ->
  `NUM-RLM`, and eleven others).
- `RELATIONSHIPS_DIRECTORY_NAME` (`"relationships"`) and
  `RELATIONSHIP_PREFIX` (`NUM-REL`) — every relationship entity, of any
  relationship `type` (`FEATURES_CHARACTER`, `REQUIRES`, ...), lives
  under this directory and shares this one ID prefix.
- `REQUIRED_FIELDS_BY_TYPE` — required fields per entity type, checked
  by `EntitySchemaValidator`.
- `BASELINE_REQUIRED_FIELDS` (`id`, `type`, `status`, `version`) — the
  fallback for any entity type not listed above, so schema validation
  covers every canon object rather than silently skipping unmodeled
  types.

### Realm vs. Region

A **Realm** (`NUM-RLM`) is an entire world or domain of mathematical
ideas — Realm of Change, Realm of Numbers, Realm of Geometry, Realm of
Logic, Realm of Probability — and contains many Regions. A **Region**
(`NUM-REG`) is a geographic or spatial subdivision within a Realm —
Forest of Limits, Delta River, Sigma Mountains, Calculus Academy,
Fraction Village. Canon hierarchy: `Universe -> Realm -> Region ->
{Location, Landmark}`, with Characters, Stories, and Concepts also
belonging to a Realm. `Realm` was registered in v0.14.0 on request; no
Realm content exists yet in the real knowledge base. Because it is a
brand-new type with no legacy entities to migrate, it requires `slug`
from day one (see Canon Law #1 migration status below) rather than
falling back to the graduated enforcement the ~90 pre-existing entities
still rely on.

## The Canonical Validator Framework

Every validator implements one contract:

```python
class CanonValidator(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult: ...
```

This is deliberately distinct from the generic
`numeria_forge.domain.validators.Validator` extension point (plain
error-message strings, for simple general-purpose Forge extensions):
the Canon Validation Engine needs severity-aware, structured
diagnostics — warnings as well as errors, each with a code and a
location.

`ValidationContext` wraps the loaded `Canon` (kept deliberately
minimal today so future validators can need more — workspace config, a
strict/lenient flag — without changing every validator's signature
again). `ValidationResult` is one validator's outcome: its `name` plus
a tuple of `Diagnostic`s, with derived `errors` / `warnings` /
`success` properties. Both `ValidationContext` and `ValidationResult`
are new in v0.14.0, replacing validators calling each other directly
with plain `Canon` arguments.

`Diagnostic` / `Severity` are the single shared type used by both this
engine and the Compiler (`numeria_forge.diagnostics` — see
`FORGE_COMPILER.md`).

## The ten default validators

`create_default_canon_validators()` returns this tuple, in roughly
pipeline order — load integrity and identity checks first, since
everything else assumes IDs are trustworthy, then cross-references,
then business rules and semantics last:

| # | Validator | Code | Checks |
|---|---|---|---|
| 1 | `LoadIntegrityValidator` | `canon.load-integrity` | Surfaces every non-duplicate `CanonLoadError` (unreadable file, bad YAML, missing id/type, ...) as an `ERROR` diagnostic. |
| 2 | `DuplicateIdValidator` | `canon.duplicate-id` | Surfaces `CanonLoadError`s with code `DUPLICATE_ID` specifically — the same underlying load errors as #1, but filtered to just this one concern so it can be reasoned about independently. |
| 3 | `EntitySchemaValidator` | `canon.schema` | Every non-relationship entity has the fields `REQUIRED_FIELDS_BY_TYPE` (or `BASELINE_REQUIRED_FIELDS`) demands for its type. |
| 4 | `IdentityValidator` | `canon.identity` | The entity's `id` matches the required prefix pattern for its type (or `RELATIONSHIP_PREFIX` if it's a relationship); flags duplicate display names within a type as a `WARNING`. |
| 5 | `CanonLawValidator` | `canon.law-1-identity-agreement` | Canon Law #1: directory name is `<id>-<slug>` exactly when the entity has a `slug`; falls back to "directory starts with id" when it doesn't (see migration status in `governance/CANON_LAWS.md`). |
| 6 | `DuplicateSlugValidator` | `canon.duplicate-slug` | No two entities of the same type share a `slug` (entities without a slug are skipped, not flagged). |
| 7 | `IdOnlyReferenceValidator` | `canon.law-3-id-only-references` | Canon Law #3: recursively walks every entity's `data` for `{id, type}`-shaped references and flags any whose `id` looks like a path (contains `/` or starts with `"knowledge"`) instead of a bare canonical ID. The entity's own top-level identity and `source_documents` path lists are excluded. |
| 8 | `RelationshipValidator` | `canon.relationships` | Every relationship entity's `type` is a known relationship type (from the ontology file, not a hardcoded list) and its `source`/`target` endpoints exist in the Canon. |
| 9 | `CanonRulesValidator` | `canon.business-rules` | Six domain business rules ported from the old `validate_canon_rules.py`: version required (error), Character needs role/domain (error), Artifact should state a purpose (warning), Book should reference concepts (warning), no self-relationships (error), `FRIEND_OF` should be bidirectional (warning). |
| 10 | `SemanticValidator` | `canon.semantic` | Lifecycle status must be `CANON` (error), version should match semver (warning if not), `REQUIRES` relationship targets must exist (error if missing, warning if they exist but aren't `CANON`). |

Two deprecated aliases exist purely for import compatibility with code
written before this split: `NamingValidator = IdentityValidator` (the
old validator used to do both the identity-format check and the
directory-agreement check; it's now two validators) and
`SlugValidator = DuplicateSlugValidator`. Likewise
`KnowledgeIntegrityValidator = LoadIntegrityValidator`. New code should
use the current names.

## Report and runner

`CanonValidationReport` (knowledge root, entity count, all
diagnostics) is what answers "is this canon internally consistent?" —
`success` is `True` iff there are zero `ERROR`-severity diagnostics
(warnings never block). It supports `to_dict()` / `to_json()` for
automation and `format_human_readable()` for terminal output, e.g.:

```
Validated 123 canonical entities under /path/to/knowledge

Canon is internally consistent. No issues found.
```

`CanonValidationRunner.run(knowledge_root)` is the domain-level entry
point that ties it all together: load the knowledge root with
`CanonLoader`, build a `ValidationContext`, run every validator, and
assemble the `CanonValidationReport`. This is what backs both `forge
validate` directly and, indirectly, `ValidateCanonStage` /
`FoundationCompiler` — both share the same default validator set via
`create_default_canon_validators()`, so a standalone `forge validate`
run and the validation step inside `forge compile` will always agree.

## The `forge validate` command

```
forge validate [path] [--json]
```

Resolves `path` to a knowledge root (via `numeria.yaml` if present, a
`knowledge/` subdirectory, or the path itself), runs
`CanonValidationRunner`, and prints the human-readable or JSON report.
Exits with code 1 if the Canon is not internally consistent. Verified
against the real 123-entity knowledge base as of this writing: `0`
load errors, `0` validation errors or warnings.
