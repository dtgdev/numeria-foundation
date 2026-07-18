#!/bin/bash
set -e

BASE="knowledge/concepts/derivative"

mkdir -p "$BASE"

############################################
# README
############################################
cat > "$BASE/README.md" <<'MD'
# Derivative

Canonical Concept ID: calculus.derivative

## Mission

Derivative is the canonical representation of instantaneous change within the Numeria universe.

It is the reference implementation for every future mathematical concept.

## Core Question

How fast is something changing right now?

## Character

Detective Derivative

## Symbol

d/dx

## Domain

Calculus

## Status

Canonical
MD

############################################
# concept.yaml
############################################
cat > "$BASE/concept.yaml" <<'YAML'
id: calculus.derivative

name: Derivative

version: 1.0.0

status: canonical

domain: Calculus

subdomain: Differential Calculus

difficulty: Intermediate

symbol:
  primary: d/dx
  alternate:
    - f'(x)
    - dy/dx

meaning:
  short: Measures instantaneous change.
  slogan: Every change leaves a trail.

essential_question:
  How can we measure change at one exact instant?

character: detective-derivative

artifact: silver-delta-necklace

location: kingdom-of-limits

book: detective-derivative-book-1
YAML

############################################
# mathematics.md
############################################
cat > "$BASE/mathematics.md" <<'MD'
# Mathematical Truth

## Formal Definition

A derivative measures the instantaneous rate of change of a function with respect to one of its variables.

Geometrically it is the slope of the tangent line.

Physically it represents quantities such as velocity and acceleration.

Economically it models marginal change.

Biologically it models growth.

Engineering uses derivatives to understand changing systems.
MD

############################################
# intuition.md
############################################
cat > "$BASE/intuition.md" <<'MD'
# Intuition

Imagine riding a bicycle.

Average speed tells you how fast you traveled during the trip.

A derivative asks a different question.

How fast are you moving at this exact instant?

That is Detective Derivative's specialty.

He solves mysteries of change.
MD

############################################
# learning.md
############################################
cat > "$BASE/learning.md" <<'MD'
# Learning Journey

1. Observe change.

2. Compare slow and fast change.

3. Understand average change.

4. Ask what happens at one exact moment.

5. Introduce tangent lines.

6. Discover derivatives.

7. Apply derivatives to real-world problems.
MD

############################################
# misconceptions.md
############################################
cat > "$BASE/misconceptions.md" <<'MD'
# Common Misconceptions

## A derivative is just another equation.

No.

A derivative is a measurement of change.

---

## A derivative always means speed.

No.

Speed is only one application.

---

## Average change and instantaneous change are the same.

No.

They answer different questions.
MD

############################################
# relationships.yaml
############################################
cat > "$BASE/relationships.yaml" <<'YAML'
depends_on:
  - function
  - limit

supports:
  - tangent_line
  - optimization
  - velocity
  - acceleration
  - differential_equations

represented_by:
  - d/dx
  - dy/dx
  - f'(x)

embodied_by:
  - detective-derivative

artifact:
  - silver-delta-necklace

location:
  - kingdom-of-limits
YAML

############################################
# media.yaml
############################################
cat > "$BASE/media.yaml" <<'YAML'
stories:
  - The Mystery of Constant Change
  - The Fastest Sunflower
  - The Secret of the Silver Delta

animations:
  - Tangent Line Adventure

games:
  - Detective Derivative

worksheets:
  - Discovering Change

videos:
  - What Is a Derivative?
YAML

############################################
# ai-profile.md
############################################
cat > "$BASE/ai-profile.md" <<'MD'
# AI Teaching Profile

Teaching Style

- Curious
- Patient
- Encouraging

Preferred Analogies

- Speedometer
- Growing sunflower
- Rocket launch
- River flow

Teaching Goal

Help learners discover the derivative instead of memorizing it.
MD

############################################
# history.md
############################################
cat > "$BASE/history.md" <<'MD'
# History

Version 1.0.0

First canonical concept created for Numeria.

Reference implementation for all future concepts.
MD

############################################
# references.md
############################################
cat > "$BASE/references.md" <<'MD'
# References

- Isaac Newton
- Gottfried Wilhelm Leibniz
- Modern Calculus Textbooks
- Educational Research on Conceptual Learning
MD

echo ""
echo "========================================"
echo "Derivative concept package created."
echo "Location:"
echo "  $BASE"
echo "========================================"
