from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from dependency_injector.wiring import inject, Provide

from src.app.core.container import Container
from src.app.application.location.services import LocationService
from src.app.api.v1.schemas.common import BaseResponse, ListResponse
from src.app.api.v1.schemas.location import (
    LocationRead,
    LocationCreate,
    LocationUpdate,
)
from src.app.api.v1.schemas.auth import TokenPayload
from src.app.api.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=ListResponse[LocationRead])
@inject
async def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    location_service: LocationService = Depends(Provide[Container.location_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    locations, total = await location_service.get_locations(skip=skip, limit=limit)
    return ListResponse(
        total=total, data=[LocationRead.model_validate(l) for l in locations]
    )


@router.post("", response_model=BaseResponse[LocationRead])
@inject
async def create_location(
    location_in: LocationCreate,
    location_service: LocationService = Depends(Provide[Container.location_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    location = await location_service.create_location(
        name=location_in.name,
        note=location_in.note,
        creator_id=current_user.sub,
    )
    return BaseResponse(data=LocationRead.model_validate(location))


@router.get("/{location_id}", response_model=BaseResponse[LocationRead])
@inject
async def get_location(
    location_id: UUID,
    location_service: LocationService = Depends(Provide[Container.location_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return BaseResponse(data=LocationRead.model_validate(location))


@router.put("/{location_id}", response_model=BaseResponse[LocationRead])
@inject
async def update_location(
    location_id: UUID,
    location_in: LocationUpdate,
    location_service: LocationService = Depends(Provide[Container.location_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    location = await location_service.update_location(
        location_id=location_id,
        name=location_in.name,
        note=location_in.note,
        updater_id=current_user.sub,
    )
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return BaseResponse(data=LocationRead.model_validate(location))


@router.delete("/{location_id}", response_model=BaseResponse[bool])
@inject
async def delete_location(
    location_id: UUID,
    location_service: LocationService = Depends(Provide[Container.location_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    success = await location_service.delete_location(location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
    return BaseResponse(data=True)
