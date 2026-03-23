from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.like import Like
from app.models.post import Post


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self) -> tuple[Select, object]:
        likes_count = func.count(Like.id).label("likes_count")
        query = (
            select(Post, likes_count)
            .outerjoin(Like, Like.post_id == Post.id)
            .options(selectinload(Post.author))
            .group_by(Post.id)
        )
        return query, likes_count

    async def create(self, *, title: str, content: str, author_id: int) -> Post:
        post = Post(title=title, content=content, author_id=author_id)
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def get_with_likes(self, post_id: int) -> tuple[Post, int] | None:
        query, _likes_count = self._base_query()
        result = await self.session.execute(query.where(Post.id == post_id))
        row = result.first()
        if row is None:
            return None
        return row[0], row[1]

    async def list_with_likes(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
        sort: str = "created_at",
    ) -> tuple[list[tuple[Post, int]], int]:
        query, likes_count = self._base_query()
        count_query = select(func.count(Post.id))

        if search:
            criteria = or_(
                Post.title.ilike(f"%{search}%"), Post.content.ilike(f"%{search}%")
            )
            query = query.where(criteria)
            count_query = count_query.where(criteria)

        if sort == "likes":
            query = query.order_by(likes_count.desc(), Post.id.desc())
        else:
            query = query.order_by(Post.created_at.desc(), Post.id.desc())

        query = query.limit(limit).offset(offset)

        rows = (await self.session.execute(query)).all()
        total = (await self.session.execute(count_query)).scalar_one()
        return [(row[0], row[1]) for row in rows], total

    async def get_for_update(self, post_id: int) -> Post | None:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)
