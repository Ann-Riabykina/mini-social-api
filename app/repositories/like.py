from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Like


class LikeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_and_post(self, user_id: int, post_id: int) -> Like | None:
        result = await self.session.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, post_id: int) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.session.add(like)
        await self.session.flush()
        return like

    async def delete_by_user_and_post(self, user_id: int, post_id: int) -> bool:
        result = await self.session.execute(
            delete(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        return result.rowcount > 0
