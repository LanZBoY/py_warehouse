from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.app.core.security.auth import decode_access_token
from src.app.api.v1.schemas.auth import TokenPayload

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    驗證 Bearer Token 並回傳 Token Payload 物件。
    """
    token = credentials.credentials
    payload_data = decode_access_token(token)
    if not payload_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    try:
        return TokenPayload(**payload_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def admin_required(
    current_user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """
    確保目前使用者具備管理員權限。
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privilege required",
        )
    return current_user
