# ADR-0006: Extension Framework

## Status

Accepted

## Version

Numeria Forge v0.7

## Context

Numeria Forge has evolved from a package compiler into a workspace build system.

Future capabilities should not require modifying Forge Core.

Examples include:

- new artifact types
- template libraries
- validators
- AI generators
- compiler stages
- CLI commands
- workspace discovery rules

Rather than embedding these capabilities into Forge Core, they should be contributed through a stable extension API.

## Decision

Forge will expose an Extension Framework.

Extensions register capabilities during startup.

Forge Core owns orchestration.

Extensions own behavior.

## Architecture

                    Forge Core
                         │
                         ▼
                 Extension Manager
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 Artifact Providers  Template Providers  Validators
        │                │                │
        ├────────────────┼────────────────┤
        ▼                ▼                ▼
 Compiler Hooks      CLI Commands    AI Generators

## Goals

The framework must allow extensions to contribute:

- artifacts
- templates
- validators
- compiler stages
- CLI commands
- AI generators

without changing Forge Core.

## Non-Goals

The first implementation will not include:

- dynamic installation
- dependency resolution
- version negotiation
- remote extension loading
- marketplace support

These capabilities may be added later.

## Stable API

Forge will expose a stable SDK consisting of:

- Extension
- ExtensionManager
- ExtensionContext

Everything else is considered internal implementation.

## Long-Term Vision

Forge Core becomes a platform.

Numeria capabilities become independent extensions.

Examples:

- numeria-extension-character
- numeria-extension-story
- numeria-extension-animation
- numeria-extension-assessment
- numeria-extension-ai

## Consequences

Positive:

- Highly extensible architecture
- Stable public SDK
- Independent extension development
- Smaller core
- Easier testing

Negative:

- More abstraction
- Slightly higher startup complexity
- Requires clear API versioning

## Decision Summary

Forge Core provides orchestration.

Extensions provide capabilities.

Future functionality should be implemented as extensions whenever practical.
