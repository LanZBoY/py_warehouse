from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from dependency_injector.wiring import inject, Provide

from src.app.core.container import Container
from src.app.application.item.services import ItemService
from src.app.api.v1.schemas.common import BaseResponse, ListResponse
from src.app.api.v1.schemas.item import ItemRead, ItemCreate, ItemUpdate
from src.app.api.v1.schemas.auth import TokenPayload
from src.app.api.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=ListResponse[ItemRead], summary="取得物品列表")
@inject
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    item_service: ItemService = Depends(Provide[Container.item_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    items, total = await item_service.get_items(skip=skip, limit=limit)
    return ListResponse(total=total, data=items)


@router.post("", response_model=BaseResponse[ItemRead], summary="新增物品")
@inject
async def create_item(
    item_in: ItemCreate,
    item_service: ItemService = Depends(Provide[Container.item_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    item = await item_service.create_item(
        name=item_in.name,
        note=item_in.note,
        creator_id=current_user.sub,
    )
    return BaseResponse(data=item)


@router.get("/{item_id}", response_model=BaseResponse[ItemRead], summary="取得指定物品")
@inject
async def get_item(
    item_id: UUID,
    item_service: ItemService = Depends(Provide[Container.item_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    item = await item_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return BaseResponse(data=item)


@router.put("/{item_id}", response_model=BaseResponse[ItemRead], summary="更新物品")
@inject
async def update_item(
    item_id: UUID,
    item_in: ItemUpdate,
    item_service: ItemService = Depends(Provide[Container.item_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    item = await item_service.update_item(
        item_id=item_id,
        name=item_in.name,
        note=item_in.note,
        updater_id=current_user.sub,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return BaseResponse(data=item)


@router.delete("/{item_id}", response_model=BaseResponse[bool], summary="刪除物品")
@inject
async def delete_item(
    item_id: UUID,
    item_service: ItemService = Depends(Provide[Container.item_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    success = await item_service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return BaseResponse(data=True)
