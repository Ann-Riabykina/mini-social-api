from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.db.redis import get_redis
from app.models.user import User
from app.schemas.common import MessageResponse
from app.services.likes import LikeService

router = APIRouter(prefix="/posts/{post_id}/like", tags=["likes"])


@router.post("", response_model=MessageResponse)
async def like_post(
    post_id: int,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    detail = await LikeService(session, redis).like_post(post_id, current_user)
    return MessageResponse(detail=detail)


@router.delete("", response_model=MessageResponse)
async def unlike_post(
    post_id: int,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    detail = await LikeService(session, redis).unlike_post(post_id, current_user)
    return MessageResponse(detail=detail)
