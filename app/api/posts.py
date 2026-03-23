from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.db.redis import get_redis
from app.models.user import User
from app.schemas.post import PostCreate, PostRead, PostsListResponse, PostUpdate
from app.services.posts import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> PostRead:
    return await PostService(session, redis).create_post(payload, current_user)


@router.get("", response_model=PostsListResponse)
async def list_posts(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    sort: str = Query(default="created_at", pattern="^(created_at|likes)$"),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_db),
) -> PostsListResponse:
    return await PostService(session, redis).list_posts(
        limit=limit, offset=offset, search=search, sort=sort
    )


@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: int,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_db),
) -> PostRead:
    return await PostService(session, redis).get_post(post_id)


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> PostRead:
    return await PostService(session, redis).update_post(post_id, payload, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> None:
    await PostService(session, redis).delete_post(post_id, current_user)
