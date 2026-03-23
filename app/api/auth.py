from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.auth import TokenPair, TokenRefreshRequest, UserCreate, UserLogin
from app.schemas.user import UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate, session: AsyncSession = Depends(get_db)
) -> UserRead:
    user = await AuthService(session).register(payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(
    payload: UserLogin, session: AsyncSession = Depends(get_db)
) -> TokenPair:
    return await AuthService(session).login(payload)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: TokenRefreshRequest, session: AsyncSession = Depends(get_db)
) -> TokenPair:
    return await AuthService(session).refresh(payload.refresh_token)
