from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import inject, Provide
from src.app.core.container import Container
from src.app.core.security.auth import decode_access_token
from src.app.application.user.services import UserService
from src.app.api.schemas import BaseResponse, ListResponse, UserRead
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()
security = HTTPBearer()


# --- Security Dependency ---
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


async def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privilege required",
        )
    return current_user


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
    admin_user: dict = Depends(admin_required),
):
    users, total = await user_service.get_users(skip=offset, limit=top)
    return {"total": total, "data": users}


@router.post("", response_model=BaseResponse[UserRead])
@inject
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
    admin_user: dict = Depends(admin_required),
):
    creator_id = uuid.UUID(admin_user["sub"])
    user = await user_service.create_user(
        request.username, request.password, creator_id
    )
    return {"data": user}
