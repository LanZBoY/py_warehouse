from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from src.app.core.container import Container
from src.app.application.user.services import UserService
from src.app.api.v1.schemas.common import BaseResponse, ListResponse
from src.app.api.v1.schemas.user import (
    UserRead,
    UserUpdate,
    ChangePasswordRequest,
    ResetPasswordRequest,
)
from src.app.api.v1.schemas.auth import TokenPayload
from src.app.api.dependencies import admin_required, get_current_user

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    password: str


# --- 自己 (任何登入者) ---


@router.get("/me", response_model=BaseResponse[UserRead], summary="取得自己的使用者資訊")
@inject
async def get_me(
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    user = await user_service.get_user(current_user.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(data=user)


@router.post("/me/password", response_model=BaseResponse[bool], summary="變更自己的密碼")
@inject
async def change_my_password(
    request: ChangePasswordRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: TokenPayload = Depends(get_current_user),
):
    success = await user_service.change_password(
        user_id=current_user.sub,
        old_password=request.old_password,
        new_password=request.new_password,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect or user not found",
        )
    return BaseResponse(data=True)


# --- Admin ---


@router.get("", response_model=ListResponse[UserRead], summary="取得使用者列表 (Admin)")
@inject
async def list_users(
    top: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    users, total = await user_service.get_users(skip=offset, limit=top)
    return ListResponse(total=total, data=users)


@router.post("", response_model=BaseResponse[UserRead], summary="新增使用者 (Admin)")
@inject
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    user = await user_service.create_user(
        request.username, request.password, admin_user.sub
    )
    return BaseResponse(data=user)


@router.get("/{user_id}", response_model=BaseResponse[UserRead], summary="取得指定使用者 (Admin)")
@inject
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(data=user)


@router.put("/{user_id}", response_model=BaseResponse[UserRead], summary="變更使用者角色 (Admin)")
@inject
async def update_user(
    user_id: UUID,
    request: UserUpdate,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    user = await user_service.update_role(
        user_id=user_id, role=request.role, updater_id=admin_user.sub
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(data=user)


@router.delete("/{user_id}", response_model=BaseResponse[bool], summary="刪除使用者 (Admin, 軟刪除)")
@inject
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(data=True)


@router.post("/{user_id}/reset-password", response_model=BaseResponse[bool], summary="重設指定使用者密碼 (Admin)")
@inject
async def reset_user_password(
    user_id: UUID,
    request: ResetPasswordRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    success = await user_service.reset_password(
        user_id=user_id,
        new_password=request.new_password,
        updater_id=admin_user.sub,
    )
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(data=True)
