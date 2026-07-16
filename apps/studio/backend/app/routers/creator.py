from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.creator import (
    CharacterDraft,
    CharacterValidationResult,
    PublishedCharacter,
    PublishedRelationship,
    RelationshipDraft,
    RelationshipValidationResult,
)
from app.services.creator_service import (
    character_creator_service,
    relationship_creator_service,
)


router = APIRouter(
    prefix="/api/creator",
    tags=["creator"],
)


@router.post(
    "/characters/validate",
    response_model=CharacterValidationResult,
)
def validate_character(
    draft: CharacterDraft,
) -> CharacterValidationResult:
    return character_creator_service.validate(
        draft
    )


@router.post(
    "/characters/publish",
    response_model=PublishedCharacter,
    status_code=status.HTTP_201_CREATED,
)
def publish_character(
    draft: CharacterDraft,
) -> PublishedCharacter:
    try:
        return character_creator_service.publish(
            draft
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except FileExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Character publication failed: "
                f"{exc}"
            ),
        ) from exc


@router.post(
    "/relationships/validate",
    response_model=RelationshipValidationResult,
)
def validate_relationship(
    draft: RelationshipDraft,
) -> RelationshipValidationResult:
    return relationship_creator_service.validate(
        draft
    )


@router.post(
    "/relationships/publish",
    response_model=PublishedRelationship,
    status_code=status.HTTP_201_CREATED,
)
def publish_relationship(
    draft: RelationshipDraft,
) -> PublishedRelationship:
    try:
        return (
            relationship_creator_service.publish(
                draft
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except FileExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Relationship publication failed: "
                f"{exc}"
            ),
        ) from exc
