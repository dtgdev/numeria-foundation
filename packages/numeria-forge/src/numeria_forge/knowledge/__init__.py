"""The Canonical Knowledge Model (v0.16.0).

See `numeria_forge.knowledge.model` for the full write-up and
`docs/architecture/CANONICAL_KNOWLEDGE_MODEL.md` for the design doc.
"""

from numeria_forge.knowledge.export import to_dict, to_graphml, to_json, to_yaml
from numeria_forge.knowledge.model import CanonicalKnowledgeModel
from numeria_forge.knowledge.query import KnowledgeQuery
from numeria_forge.knowledge.statistics import GraphStatistics

__all__ = [
    "CanonicalKnowledgeModel",
    "GraphStatistics",
    "KnowledgeQuery",
    "to_dict",
    "to_graphml",
    "to_json",
    "to_yaml",
]
