from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from dependency_injector.wiring import inject, Provide

from src.app.core.container import Container
from src.app.application.stock.services import StockService
from src.app.api.v1.schemas.common import BaseResponse, ListResponse
from src.app.api.v1.schemas.stock import (
    StockBalanceRead,
    StockMovementRead,
    StockMovementCreate,
    StockAdjustCreate,
)
from src.app.api.v1.schemas.auth import TokenPayload
from src.app.api.dependencies import get_current_user
from src.app.domain.stock.exceptions import InsufficientStockError

router = APIRouter()


@router.get(
    "/balances",
    response_model=ListResponse[StockBalanceRead],
    summary="取得即時存量列表",
)
@inject
async def list_balances(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    item_id: Optional[UUID] = Query(None),
    location_id: Optional[UUID] = Query(None),
    stock_service: StockService = Depends(Provide[Container.stock_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    balances, total = await stock_service.list_balances(
        skip=skip, limit=limit, item_id=item_id, location_id=location_id
    )
    return ListResponse(total=total, data=balances)


@router.get(
    "/balances/{item_id}/{location_id}",
    response_model=BaseResponse[StockBalanceRead],
    summary="取得指定 item × location 的存量",
)
@inject
async def get_balance(
    item_id: UUID,
    location_id: UUID,
    stock_service: StockService = Depends(Provide[Container.stock_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    balance = await stock_service.get_balance(item_id, location_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Stock balance not found")
    return BaseResponse(data=balance)


@router.get(
    "/movements",
    response_model=ListResponse[StockMovementRead],
    summary="取得異動流水紀錄",
)
@inject
async def list_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    item_id: Optional[UUID] = Query(None),
    location_id: Optional[UUID] = Query(None),
    stock_service: StockService = Depends(Provide[Container.stock_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    movements, total = await stock_service.list_movements(
        skip=skip, limit=limit, item_id=item_id, location_id=location_id
    )
    return ListResponse(total=total, data=movements)


@router.post(
    "/inbound",
    response_model=BaseResponse[StockMovementRead],
    summary="入庫：增加存量",
)
@inject
async def inbound(
    body: StockMovementCreate,
    stock_service: StockService = Depends(Provide[Container.stock_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    _, movement = await stock_service.inbound(
        item_id=body.item_id,
        location_id=body.location_id,
        quantity=body.quantity,
        note=body.note,
        user_id=current_user.sub,
    )
    return BaseResponse(data=movement)


@router.post(
    "/outbound",
    response_model=BaseResponse[StockMovementRead],
    summary="出庫：扣減存量",
)
@inject
async def outbound(
    body: StockMovementCreate,
    stock_service: StockService = Depends(Provide[Container.stock_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        _, movement = await stock_service.outbound(
            item_id=body.item_id,
            location_id=body.location_id,
            quantity=body.quantity,
            note=body.note,
            user_id=current_user.sub,
        )
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Insufficient stock",
                "current": e.current,
                "requested": e.requested,
            },
        )
    return BaseResponse(data=movement)


@router.post(
    "/adjust",
    response_model=BaseResponse[Optional[StockMovementRead]],
    summary="盤點調整：以目標總量產生差異流水",
)
@inject
async def adjust(
    body: StockAdjustCreate,
    stock_service: StockService = Depends(Provide[Container.stock_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    result = await stock_service.adjust(
        item_id=body.item_id,
        location_id=body.location_id,
        target_quantity=body.target_quantity,
        note=body.note,
        user_id=current_user.sub,
    )
    if result is None:
        return BaseResponse(data=None)
    _, movement = result
    return BaseResponse(data=movement)
