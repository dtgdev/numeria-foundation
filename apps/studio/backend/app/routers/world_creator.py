from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.world import (
    PublishedRegion,
    RegionDraft,
    RegionValidationResult,
)
from app.services.world_service import (
    region_creator_service,
)


router = APIRouter(
    prefix="/api/creator/world",
    tags=["world-creator"],
)


@router.post(
    "/regions/validate",
    response_model=RegionValidationResult,
)
def validate_region(
    draft: RegionDraft,
) -> RegionValidationResult:
    return region_creator_service.validate(draft)


@router.post(
    "/regions/publish",
    response_model=PublishedRegion,
    status_code=status.HTTP_201_CREATED,
)
def publish_region(
    draft: RegionDraft,
) -> PublishedRegion:
    try:
        return region_creator_service.publish(draft)
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
            detail=f"Region publication failed: {exc}",
        ) from exc
