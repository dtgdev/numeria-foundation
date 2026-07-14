from fastapi import APIRouter, HTTPException, Query

from app.models import CanonEntity, CanonRelationship, CanonSummary
from app.services import graph_service


router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/summary", response_model=CanonSummary)
def graph_summary() -> CanonSummary:
    return graph_service.get_summary()


@router.get("/entities", response_model=list[CanonEntity])
def graph_entities(
    entity_type: str | None = Query(default=None, alias="type"),
) -> list[CanonEntity]:
    entities = graph_service.get_entities()

    if entity_type is None:
        return entities

    return [
        entity for entity in entities if entity.type == entity_type
    ]


@router.get(
    "/relationships",
    response_model=list[CanonRelationship],
)
def graph_relationships(
    relationship_type: str | None = Query(default=None, alias="type"),
) -> list[CanonRelationship]:
    relationships = graph_service.get_relationships()

    if relationship_type is None:
        return relationships

    return [
        relationship
        for relationship in relationships
        if relationship.type == relationship_type
    ]


@router.get("/entity/{entity_id}", response_model=CanonEntity)
def graph_entity(entity_id: str) -> CanonEntity:
    entity = graph_service.get_entity(entity_id)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Canon entity not found",
        )

    return entity


@router.get("/entity/{entity_id}/neighbors")
def graph_entity_neighbors(entity_id: str) -> dict[str, object]:
    if graph_service.get_entity(entity_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Canon entity not found",
        )

    return graph_service.get_neighbors(entity_id)


@router.post("/refresh", response_model=CanonSummary)
def refresh_graph() -> CanonSummary:
    return graph_service.refresh().summary
