Numeria Authoring Templates

Templates provide reusable starting structures for canonical Numeria entities and experiences.

They are designed to help contributors create consistent packages without starting from an empty directory.

Available Templates

templates/
├── concept/
├── character/
├── story/
└── lesson/

How to Use a Template

Copy the appropriate template into the destination directory.

Example:

cp -R templates/concept \
  knowledge/concepts/NUM-CON-000002-function

Then replace all placeholders with the canonical entity information.

Important Rules

* Templates are not canonical content.
* Placeholder values must be removed.
* Every canonical entity must receive a permanent identifier.
* Structured files must satisfy the applicable schema.
* Supporting Markdown must follow the relevant Numeria Standard.
* New canonical entities must follow the review lifecycle.

Template and Schema Difference

Templates help humans author content.

Schemas help machines validate content.

Both should remain aligned.