# Numeria Learning Graph Principles

Version: 1.0.0

## Purpose

The Numeria Learning Graph represents mathematical knowledge, creative canon,
learning resources, and educational relationships as one connected system.

The graph must explain not only what exists, but also how each entity helps a
learner understand mathematics.

## Core Principle

Every important Numeria object is a node.

Every meaningful connection is a relationship.

## Node Requirements

Every node must have:

- A globally unique ID
- A registered node type
- A human-readable name
- A lifecycle status
- A semantic version
- A canonical source file or package
- At least one meaningful relationship when appropriate

## Relationship Requirements

Every relationship must have:

- A source node
- A registered relationship type
- A target node
- A clear semantic meaning
- Optional educational or creative context

## Global ID Convention

Numeria IDs use lowercase dot-separated namespaces.

Examples:

```text
concept.calculus.derivative
concept.calculus.limit
concept.functions.function
character.detective-derivative
artifact.silver-delta-necklace
location.kingdom-of-limits
story.derivative.book-1
lesson.derivative.introduction
assessment.derivative.foundations
Recommended pattern: entity-type.domain-or-family.name
Learning Graph Principle

The graph is not merely a database of facts.

It must support questions such as:

* What should a learner understand first?
* Which misconception blocks progress?
* Which character embodies this concept?
* Which story introduces the idea?
* Which activity practices the skill?
* Which assessment demonstrates mastery?
* Which concept should the learner explore next?

Canonical Ownership

Entity packages own their canonical content.

The graph owns the canonical connections between entities.

Local relationship files may provide package-level views, but the graph registry
is the authoritative cross-package relationship source.

Golden Rule

A relationship belongs in the Numeria Learning Graph when it helps explain
mathematical meaning, learning progression, creative canon, or real-world use.
