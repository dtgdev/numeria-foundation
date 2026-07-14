from __future__ import annotations

from functools import lru_cache

from app.core import load_canon
from app.models import CanonEntity, CanonGraph, CanonRelationship, CanonSummary


class GraphService:
    @staticmethod
    @lru_cache(maxsize=1)
    def graph() -> CanonGraph:
        return load_canon()

    def refresh(self) -> CanonGraph:
        self.graph.cache_clear()
        return self.graph()

    def get_summary(self) -> CanonSummary:
        return self.graph().summary

    def get_entities(self) -> list[CanonEntity]:
        return self.graph().entities

    def get_relationships(self) -> list[CanonRelationship]:
        return self.graph().relationships

    def get_entity(self, entity_id: str) -> CanonEntity | None:
        return next(
            (
                entity
                for entity in self.graph().entities
                if entity.id == entity_id
            ),
            None,
        )

    def get_neighbors(self, entity_id: str) -> dict[str, object]:
        graph = self.graph()

        relationships = [
            relationship
            for relationship in graph.relationships
            if relationship.source == entity_id
            or relationship.target == entity_id
        ]

        neighbor_ids = {
            relationship.target
            if relationship.source == entity_id
            else relationship.source
            for relationship in relationships
        }

        neighbors = [
            entity
            for entity in graph.entities
            if entity.id in neighbor_ids
        ]

        return {
            "entity_id": entity_id,
            "neighbors": neighbors,
            "relationships": relationships,
        }


graph_service = GraphService()
