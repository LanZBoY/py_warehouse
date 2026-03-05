from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from src.app.core.container import Container
from src.app.application.user.services import AuthService
from src.app.api.v1.schemas.common import BaseResponse
from src.app.api.v1.schemas.auth import LoginRequest

router = APIRouter()


@router.post("/login", response_model=BaseResponse[str])
@inject
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    token = await auth_service.authenticate(request.username, request.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"data": token}
