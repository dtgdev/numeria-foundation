# The Laws of the Compiler

Where `CANON_LAWS.md` records the binding rules the Canon's *data*
must obey, this document records the binding rules the Forge
*Compiler* itself must obey -- properties of the compilation process,
not the content being compiled.

---

## Compiler Law #1 — Compilation Is Deterministic

> Same Canon + Same Compiler Version = Identical Output.

Concretely:

- No timestamps in generated output or reports.
- No random IDs.
- No hidden AI calls during compilation.
- No network dependence.
- Everything reproducible: compiling the same Canon twice, on the same
  compiler version, produces byte-identical output.

### Why

This is what makes versioned educational content, reproducible builds,
CI/CD, and eventually certification or regulated educational workflows
possible. A compiler whose output depends on *when* or *where* it ran
can't be trusted to answer "did this content actually change" -- every
diff would be suspect.

### Enforcement

Two layers:

1. **Code audit.** No module under `numeria_forge` imports
   `datetime`/`time`, `uuid`/`random`/`secrets`, or any networking
   library (`requests`, `urllib`, `httpx`, `aiohttp`, raw `socket`).
   No AI provider (`numeria_forge.ai`) is wired into
   `FoundationCompiler`'s pipeline -- AI-assisted generation is a
   separate, explicitly-invoked path (`forge new concept`, etc.), never
   something `forge compile` triggers on its own. Every place that
   groups or looks up canonical data by a derived key uses a `dict`
   (Python dicts preserve insertion order) or a `list`, never a
   `set`/`frozenset` whose contents are iterated directly into output
   -- `set` iteration order depends on `PYTHONHASHSEED` and is *not*
   guaranteed stable across process runs, unlike `dict`. Where a `set`
   is used at all (e.g. `SemanticGraph.adjacency`'s `wanted` type
   filter), it's used only for membership testing, never iterated.
   File system walks (`CanonLoader`) sort paths explicitly rather than
   relying on OS-reported directory order.
2. **A regression test that proves it, not just asserts it.**
   `tests/integration/test_compiler_determinism.py` builds an identical
   fixture Canon in two independent directories, compiles both, and
   asserts the `CompilationReport` JSON, every generated artifact's
   content, the topological order, and every byte written under
   `build/` are identical between the two runs. A second test compiles
   the same directory twice in a row and asserts the same. If a future
   change introduces non-determinism, this is where it fails.

### Verified (as of 2026-07-22)

Audited the full `numeria_forge` compiler and semantics packages
against the above; found no violations. Ran the determinism test
against both a synthetic fixture and the real 123-entity knowledge
base (two consecutive `FoundationCompiler().compile()` calls,
comparing `report.to_json()`) -- identical both times.

### Known gap (not a Law #1 violation, but adjacent)

`build/` is never cleared before a compile, only overwritten
file-by-file. If a Canon change *removes* an entity (or a manifest
output), the previously-generated file for it is not deleted --
`build/` can accumulate stale, orphaned files across runs with
different Canon content. This doesn't break determinism (recompiling
the *same* Canon still produces identical output), but it does mean
`build/` isn't a strict function of "the current Canon" the way this
Law's spirit implies. Worth a `--clean` flag or a full `build/` wipe
before every compile, if that becomes a real problem.
