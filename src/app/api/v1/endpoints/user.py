from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from src.app.core.container import Container
from src.app.application.user.services import UserService
from src.app.api.v1.schemas.common import BaseResponse, ListResponse
from src.app.api.v1.schemas.user import UserRead
from src.app.api.v1.schemas.auth import TokenPayload
from src.app.api.dependencies import admin_required
from pydantic import BaseModel

router = APIRouter()


# --- User Management Endpoints ---
class CreateUserRequest(BaseModel):
    username: str
    password: str


@router.get("", response_model=ListResponse[UserRead])
@inject
async def list_users(
    top: int = 10,
    offset: int = 0,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    users, total = await user_service.get_users(skip=offset, limit=top)
    return {"total": total, "data": users}


@router.post("", response_model=BaseResponse[UserRead])
@inject
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: TokenPayload = Depends(admin_required),
):
    user = await user_service.create_user(
        request.username, request.password, admin_user.sub
    )
    return {"data": user}
