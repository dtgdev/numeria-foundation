Numeria Repository Guide

Status: Active
Version: 0.1
Project: Project Atlas

Purpose

This guide explains where artifacts belong within the Numeria Foundation repository.

The repository separates:

1. Governance and architecture
2. Canonical knowledge
3. Human-readable mathematical reference
4. Creative and educational experiences
5. Technology and delivery systems
6. Project history

This separation protects the distinction between timeless knowledge and the experiences created from it.

⸻

Repository Model

Architecture
     ↓
Canonical Knowledge
     ↓
Educational IP and Learning Experiences
     ↓
Technology and Delivery

Core Principle

Knowledge is authored once. Experiences reference it everywhere.

⸻

Governance and Architecture

docs/

Contains human-readable documents explaining Numeria’s mission, structure, governance, architecture, and roadmap.

Examples:

* Founder’s Guide
* Foundation charter
* Numeria IP strategy
* Numeria Platform strategy
* Architecture
* Roadmap
* Repository guide
* ADR guide

This directory explains how Numeria works and why important decisions were made.

⸻

docs/adr/

Contains Architecture Decision Records.

ADRs preserve major decisions that affect the long-term design of Numeria.

Examples:

* Semantic Core as the source of truth
* Stable identifier conventions
* Entity lifecycle
* Separation of mathematical, canonical, and story truth

Accepted ADRs should not be silently rewritten when the architecture changes. A new ADR should supersede the previous decision.

⸻

ontology/

Defines what kinds of entities and relationships are allowed to exist.

Examples:

* Concept
* Character
* Story
* Lesson
* Curriculum
* Media
* Organization
* Location

The ontology defines the vocabulary and semantic structure of Numeria.

It does not contain the actual canonical instances.

For example:

ontology/entities/concept.yaml

defines what a mathematical concept is.

It does not define the derivative itself.

⸻

schemas/

Contains machine-readable validation rules.

Schemas define the required structure for canonical entities.

Examples:

schemas/concept.schema.yaml
schemas/character.schema.yaml
schemas/story.schema.yaml
schemas/lesson.schema.yaml

Schemas answer questions such as:

* Which fields are required?
* What data types are allowed?
* Which status values are valid?
* How should identifiers be formatted?

⸻

standards/

Contains official Numeria production standards.

Standards define how contributors should create artifacts consistently.

Examples:

* Entity package standard
* Character standard
* Story standard
* Lesson standard
* Mathematical writing standard
* Artwork standard

Architecture decisions explain why a rule exists.

Standards explain how contributors must follow it.

⸻

templates/

Contains reusable starting structures for authors and contributors.

Templates are human authoring tools.

Examples:

templates/concept/
templates/character/
templates/story/
templates/lesson/

A contributor should copy the relevant template when creating a new canonical package.

Templates are not canonical entities themselves.

⸻

Canonical Knowledge

knowledge/

Contains canonical semantic entity instances.

This is the structured source of truth used by the Semantic Core.

Examples:

knowledge/concepts/
knowledge/characters/
knowledge/stories/
knowledge/education/
knowledge/media/
knowledge/relationships/

Each important entity may use a package directory containing structured YAML and supporting Markdown.

Example:

knowledge/concepts/NUM-CON-000001-derivative/
├── entity.yaml
├── mathematics.md
├── education.md
├── examples.md
├── applications.md
├── references.md
└── changelog.md

The YAML record contains machine-readable semantic truth.

The Markdown files provide human-readable supporting knowledge.

⸻

knowledge/concepts/

Contains canonical mathematical concept entities.

Examples:

* Derivative
* Integral
* Limit
* Function
* Slope
* Fraction
* Prime Number

Concept entities must remain independent of specific stories and media.

⸻

knowledge/characters/

Contains canonical semantic character entities.

A character may represent one or more mathematical concepts but must never replace their mathematical definitions.

Example:

NUM-CHR-000001-detective-derivative/

⸻

knowledge/stories/

Contains canonical semantic metadata about official stories.

The complete manuscript belongs in the appropriate experience directory, such as books/.

The knowledge record connects the story to concepts, characters, educational objectives, media adaptations, and assessments.

⸻

knowledge/education/

Contains canonical educational entities.

Examples:

* Learning objectives
* Prerequisites
* Misconceptions
* Vocabulary
* Grade bands
* Curriculum mappings
* Assessments
* Learning progressions

⸻

knowledge/relationships/

Contains canonical relationship definitions or approved relationship instances that connect entities.

Examples:

* represents
* prerequisiteFor
* teaches
* appearsIn
* assessedBy
* adaptedAs

⸻

Mathematical Reference

mathematics/

Contains rich, human-readable mathematical reference material.

This directory is written for mathematicians, educators, learners, and contributors.

It may include:

* Formal definitions
* Intuition
* Proofs
* Worked examples
* Historical context
* Diagrams
* Applications
* References

Example:

mathematics/calculus/derivative.md

The mathematics/ directory and the knowledge/ directory serve different purposes:

Directory	Purpose
mathematics/	Rich human-readable mathematical reference
knowledge/	Structured machine-readable canonical entities

⸻

Educational IP and Experiences

characters/

Contains creative production assets for characters.

Examples:

* Character design sheets
* Expression guides
* Pose references
* Dialogue samples
* Approved illustrations
* Voice direction
* Animation references

The canonical semantic character identity remains under knowledge/characters/.

⸻

world/

Contains Numeria’s fictional universe.

Examples:

* Maps
* Kingdoms
* Cities
* Organizations
* History
* Lore
* Cultural traditions
* World timelines

Canonical semantic world entities may also be represented under knowledge/.

⸻

books/

Contains book manuscripts and publishing artifacts.

Examples:

* Outlines
* Chapters
* Editing notes
* Page plans
* Print layouts
* Publishing metadata

Books reference canonical concepts and characters rather than redefining them.

⸻

animation/

Contains animation production artifacts.

Examples:

* Episode outlines
* Scripts
* Storyboards
* Animatics
* Voice direction
* Scene plans

⸻

games/

Contains interactive game designs and implementations.

Examples:

* Game mechanics
* Level designs
* Puzzle systems
* Learning mappings
* Source code
* Game assets

⸻

curriculum/

Contains curriculum frameworks and educational sequences.

Examples:

* Grade-level progressions
* Standards mappings
* Units
* Scope and sequence
* Teacher guides

⸻

lessons/

Contains individual learner-facing or classroom lessons.

Lessons reference canonical concepts, learning objectives, activities, and assessments.

⸻

activities/

Contains hands-on, collaborative, or exploratory learning activities.

⸻

worksheets/

Contains printable or interactive practice materials.

⸻

artwork/

Contains official and experimental artwork.

Artwork should clearly indicate whether it is:

* Experimental
* Under review
* Canonical
* Deprecated
* Archived

⸻

music/

Contains musical themes, songs, scores, and audio concepts.

⸻

Technology and Delivery

ai/

Contains Numeria AI architecture and implementation artifacts.

Examples:

* Tutor behavior
* Prompt systems
* Retrieval workflows
* Safety rules
* Character conversation policies
* Evaluation datasets
* Personalization logic

AI outputs do not automatically become canonical.

⸻

api/

Contains application programming interfaces and service contracts.

These interfaces allow websites, applications, games, AI systems, and external tools to consume the Numeria Platform.

⸻

website/

Contains the public web experience.

⸻

Community and Governance Support

community/

Contains contributor and community resources.

Examples:

* Contributor onboarding
* Community proposals
* Translation guidance
* Educator participation
* Artist participation
* Student contribution programs

⸻

legal/

Contains legal and intellectual property policies.

Examples:

* Licensing
* Trademark policy
* Contributor agreements
* Educational-use policies
* Brand-use guidance

⸻

research/

Contains research supporting Numeria’s educational methods.

Examples:

* Learning science
* Cognitive psychology
* Story-based learning
* Memory
* Mathematics education
* AI tutoring
* Accessibility

Research material should distinguish original Numeria research from external references.

⸻

Project History

journal/

Contains founder and project journal entries.

The journal preserves:

* Important milestones
* Founding reflections
* Major decisions
* Historical context
* Creative discoveries
* Project lessons

Journal entries document history but do not override canonical architecture or knowledge.

⸻

archive/

Contains superseded or retired artifacts retained for historical purposes.

Archived content must not be presented as current canonical material.

⸻

Where Should a New File Go?

Use these questions:

Is it explaining why Numeria exists or how it is governed?

Place it in:

docs/

Is it recording a major architectural decision?

Place it in:

docs/adr/

Is it defining what kinds of entities or relationships may exist?

Place it in:

ontology/

Is it defining validation requirements?

Place it in:

schemas/

Is it defining a required production practice?

Place it in:

standards/

Is it a reusable authoring starting point?

Place it in:

templates/

Is it canonical structured knowledge?

Place it in:

knowledge/

Is it a deep human-readable mathematical explanation?

Place it in:

mathematics/

Is it something a learner reads, watches, plays, or uses?

Place it in the appropriate experience directory:

books/
animation/
games/
lessons/
activities/
worksheets/
website/

Is it source code or platform delivery infrastructure?

Place it in:

ai/
api/
website/
games/

depending on its responsibility.

⸻

Avoiding Duplication

A mathematical definition should not be copied independently into multiple stories, lessons, and applications.

Instead:

1. Define the canonical concept in knowledge/.
2. Provide the rich reference in mathematics/.
3. Reference the concept ID from experiences.
4. Adapt the explanation to the audience without changing the underlying truth.

⸻

Final Rule

When uncertain where an artifact belongs, ask:

Is this defining truth, defining rules, or creating an experience?

* Truth belongs in knowledge/.
* Rules belong in docs/, ontology/, schemas/, or standards/.
* Experiences belong in books, lessons, animation, games, and other delivery directories.

This separation keeps Numeria coherent as it grows.