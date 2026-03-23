import json

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User
from app.repositories.post import PostRepository
from app.schemas.post import PostCreate, PostRead, PostsListResponse, PostUpdate
from app.utils.cache import build_posts_cache_key, invalidate_posts_cache


class PostService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.posts = PostRepository(session)
        self.settings = get_settings()

    @staticmethod
    def _to_read_model(post, likes_count: int) -> PostRead:
        return PostRead.model_validate(
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "author": post.author,
                "likes_count": likes_count,
            }
        )

    async def create_post(self, payload: PostCreate, current_user: User) -> PostRead:
        post = await self.posts.create(
            title=payload.title, content=payload.content, author_id=current_user.id
        )
        await self.session.commit()
        loaded = await self.posts.get_with_likes(post.id)
        await invalidate_posts_cache(self.redis)

        if loaded is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Created post could not be loaded",
            )

        return self._to_read_model(*loaded)

    async def list_posts(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
        sort: str = "created_at"
    ) -> PostsListResponse:
        cache_key = build_posts_cache_key(
            {"limit": limit, "offset": offset, "search": search, "sort": sort}
        )
        cached = await self.redis.get(cache_key)
        if cached:
            return PostsListResponse.model_validate_json(cached)

        rows, total = await self.posts.list_with_likes(
            limit=limit, offset=offset, search=search, sort=sort
        )
        response = PostsListResponse(
            items=[
                self._to_read_model(post, likes_count) for post, likes_count in rows
            ],
            limit=limit,
            offset=offset,
            total=total,
        )
        await self.redis.set(
            cache_key,
            response.model_dump_json(),
            ex=self.settings.posts_cache_ttl_seconds,
        )
        return response

    async def get_post(self, post_id: int) -> PostRead:
        row = await self.posts.get_with_likes(post_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return self._to_read_model(*row)

    async def update_post(
        self, post_id: int, payload: PostUpdate, current_user: User
    ) -> PostRead:
        post = await self.posts.get_for_update(post_id)
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )

        if payload.title is not None:
            post.title = payload.title
        if payload.content is not None:
            post.content = payload.content

        await self.session.commit()
        await self.session.refresh(post)
        await invalidate_posts_cache(self.redis)
        row = await self.posts.get_with_likes(post.id)

        if row is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Updated post could not be loaded",
            )

        return self._to_read_model(*row)

    async def delete_post(self, post_id: int, current_user: User) -> None:
        post = await self.posts.get_for_update(post_id)
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )

        await self.posts.delete(post)
        await self.session.commit()
        await invalidate_posts_cache(self.redis)
