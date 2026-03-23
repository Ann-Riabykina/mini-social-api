from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User
from app.repositories.like import LikeRepository
from app.repositories.post import PostRepository
from app.utils.cache import invalidate_posts_cache


class LikeService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.likes = LikeRepository(session)
        self.posts = PostRepository(session)
        self.settings = get_settings()

    async def _check_rate_limit(self, user_id: int) -> None:
        key = f"rate-limit:likes:{user_id}"
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, self.settings.rate_limit_window_seconds)
        if current > self.settings.rate_limit_max_likes:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Like rate limit exceeded",
            )

    async def like_post(self, post_id: int, current_user: User) -> str:
        await self._check_rate_limit(current_user.id)
        post = await self.posts.get_for_update(post_id)
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        try:
            await self.likes.create(current_user.id, post_id)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            return "Post already liked"

        await invalidate_posts_cache(self.redis)
        return "Post liked"

    async def unlike_post(self, post_id: int, current_user: User) -> str:
        post = await self.posts.get_for_update(post_id)
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        await self.likes.delete_by_user_and_post(current_user.id, post_id)
        await self.session.commit()
        await invalidate_posts_cache(self.redis)
        return "Post unliked"
