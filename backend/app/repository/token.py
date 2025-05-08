from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Token
from app.schemas.token import TokenScheme


class TokenRepository:
    @staticmethod
    async def save(session: AsyncSession, token: TokenScheme):
        new_token = Token(
            jti=token.jti,
            user_id=token.user_id,
            fp=token.fp.get_secret_value(),
            expires_at=token.expires_at,
            created_at=token.created_at,
        )
        session.add(new_token)
        await session.flush()
        await session.refresh(new_token)

    @staticmethod
    async def revoke(session: AsyncSession, jti: str):
        await session.execute(
            update(Token).where(Token.jti == jti).values(revoked=True)
        )
        await session.commit()

    @staticmethod
    async def is_allowed(session: AsyncSession, fp: str) -> bool:
        row = await session.scalar(
            select(Token.revoked).where(Token.fp == fp, Token.expires_at > func.now())
        )
        return row is not None and not row

    @staticmethod
    async def cleanup(session: AsyncSession):
        await session.execute(delete(Token).where(Token.expires_at < func.now()))
        await session.commit()


token_repo = TokenRepository()
