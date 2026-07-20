# ADR-0005: Workspace and Multi-Package Compilation

## Status

Accepted

## Version

Numeria Forge v0.6

## Context

Numeria Forge currently compiles one package directory at a time.

This works for isolated concepts, characters, stories, and lessons, but Numeria Foundation is an interconnected educational universe containing many related packages.

Examples include:

- mathematical concepts
- characters
- stories
- lessons
- assessments
- artwork
- animation scripts
- teacher resources

Compiling each package manually does not scale and makes it difficult to manage the Numeria universe as one coherent project.

Numeria Forge therefore needs a workspace abstraction that can discover, compile, and report on multiple packages in a single build.

## Decision

Numeria Forge will introduce a workspace model in v0.6.

A workspace is a directory containing:

- a `workspace.yaml` file
- one or more Numeria packages
- optional build and cache directories

Example:

```text
numeria-foundation/
├── workspace.yaml
├── packages/
│   ├── concepts/
│   │   ├── derivative/
│   │   ├── integral/
│   │   └── limit/
│   ├── characters/
│   ├── stories/
│   └── lessons/
└── build/
Each package remains independently compilable using the existing compiler pipeline.

The workspace compiler coordinates package compilation but does not replace the package compiler.

Workspace Manifest

The workspace will be defined by workspace.yaml.

Initial format:

schema_version: "1.0"

workspace:
  id: numeria-foundation
  name: Numeria Foundation
  version: "0.1.0"

packages:
  - packages/concepts/derivative
  - packages/concepts/integral
  - packages/concepts/limit
Future versions may support glob-based discovery:

packages:
  - packages/concepts/*
  - packages/characters/*
  - packages/stories/*
  - packages/lessons/*

Workspace
WorkspaceMetadata
WorkspacePackage

Workspace

Represents the complete loaded workspace.

Responsibilities:

* hold workspace metadata
* contain discovered packages
* preserve the workspace root directory

WorkspaceMetadata

Contains:
* workspace ID
* name
* version

WorkspacePackage

Represents one package included in the workspace.

Contains:

* package path
* package identifier
* optional compilation result
Compilation Architecture

The architecture will be:

WorkspaceLoader
      │
      ▼
Workspace
      │
      ▼
WorkspaceCompiler
      │
      ├── Package Compiler
      ├── Package Compiler
      └── Package Compiler
              │
              ▼
        WorkspaceBuildResult

The existing package compiler remains unchanged:

LoadManifestStage
      │
      ▼
RegisterManifestArtifactsStage
      │
      ▼
RenderTemplatesStage
      │
      ▼
PublishArtifactsStage
The workspace compiler will invoke this pipeline once for each package.

Build Result

Workspace compilation will produce a result containing:

* successfully compiled packages
* failed packages
* generated artifact count
* diagnostics
* build duration

Example output:

Building Numeria Foundation...

✓ derivative
✓ integral
✓ limit

3 packages compiled
7 artifacts generated
0 warnings
0 errors

Build succeeded.

Building Numeria Foundation...

✓ derivative
✓ integral
✓ limit

3 packages compiled
7 artifacts generated
0 warnings
0 errors

Build succeeded.

Goals

The workspace implementation must:

1. Load workspace metadata from workspace.yaml.
2. Resolve package paths relative to the workspace root.
3. Compile multiple packages in one command.
4. Preserve independent package compilation.
5. Report package-level success and failure.
6. Provide a foundation for dependency resolution.
7. Provide a foundation for workspace-wide plugins.

Non-Goals

The first v0.6 implementation will not include:

* package dependency resolution
* parallel compilation
* remote packages
* package version resolution
* plugin loading
* incremental compilation
* workspace caching
* dependency graph visualization

These capabilities may be introduced in later versions.

Error Handling

Workspace loading must fail when:

* workspace.yaml does not exist
* the workspace schema is invalid
* a declared package path does not exist
* a declared package does not contain manifest.yaml

Workspace compilation should collect package-level failures so that the user receives a complete build report.

Fail-fast behavior may be added as an option later.

CLI Direction

The intended CLI will include:

forge workspace init
forge workspace build
forge workspace list
forge workspace clean
forge workspace graph

The first implementation may expose only:

forge workspace build
forge workspace list

Future Dependency Resolution

A future package manifest may declare dependencies:

dependencies:
  - numeria:concept:limit
  - numeria:character:derivative

The workspace will eventually construct a directed dependency graph and compile packages in topological order.

Dependency resolution is planned for v0.8.

Future Plugin Integration

The v0.7 plugin system will operate at workspace scope.

Plugins may contribute:

* artifact definitions
* templates
* validators
* compiler stages
* CLI commands
* package discovery rules

Workspace support is therefore implemented before the plugin system.

Consequences

Positive

* The entire Numeria universe can be built with one command.
* Existing package compilation remains reusable.
* Workspace-wide reporting becomes possible.
* Future dependencies and plugins have a natural integration point.
* Large educational projects become easier to organize.

Negative

* A second compilation orchestration layer is introduced.
* Error reporting becomes more complex.
* Build output paths must avoid collisions.
* Workspace and package configuration must remain clearly separated.

Implementation Plan

v0.6.1

Add workspace domain models.

v0.6.2

Add WorkspaceLoader.

v0.6.3

Add package validation and discovery.

v0.6.4

Add WorkspaceCompiler.

v0.6.5

Add workspace build reporting and CLI commands.

Decision Summary

Numeria Forge will support workspace-level orchestration while preserving the existing package compiler.

This creates the foundation for managing Numeria Foundation as one version-controlled, interconnected educational universe.
