from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from src.app.core.container import Container
from src.app.application.user.services import AuthService
from src.app.api.v1.schemas.common import BaseResponse
from src.app.api.v1.schemas.auth import (
    LoginRequest,
    TokenPair,
    RefreshRequest,
    LogoutRequest,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=BaseResponse[TokenPair],
    summary="登入並取得 Access / Refresh Token",
)
@inject
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    tokens = await auth_service.authenticate(request.username, request.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token, refresh_token = tokens
    return {"data": TokenPair(access_token=access_token, refresh_token=refresh_token)}


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenPair],
    summary="以 Refresh Token 換取新的 Token Pair",
)
@inject
async def refresh(
    request: RefreshRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    tokens = await auth_service.refresh(request.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    access_token, refresh_token = tokens
    return {"data": TokenPair(access_token=access_token, refresh_token=refresh_token)}


@router.post(
    "/logout",
    response_model=BaseResponse[bool],
    summary="登出並撤銷 Refresh Token",
)
@inject
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    revoked = await auth_service.logout(request.refresh_token)
    return {"data": revoked}
