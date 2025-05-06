import hashlib
import time
from datetime import UTC, datetime
from uuid import UUID, uuid4

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.token import token_repo
from app.schemas.token import TokenScheme
from app.schemas.user import UserScheme
from config import settings
from exc import InvalidCredentialsError


class TokenManager:
    @staticmethod
    async def generate_token(
        session: AsyncSession, payload: dict, user_id: int, expires_in: int = None
    ) -> str:
        jti = uuid4()
        exp_timestamp = int(time.time()) + (
            expires_in or settings.security.jwt_expires_in
        )

        payload["exp"] = exp_timestamp
        payload["iss"] = settings.security.jwt_issuer_name
        payload["type"] = "access"
        payload["jti"] = str(jti)

        try:
            new_token = jwt.encode(
                payload,
                settings.security.jwt_private_key.get_secret_value(),
                algorithm="RS256",
            )

        except Exception as e:
            raise ValueError(f"Failed to generate token: {str(e)}")

        store_token = TokenScheme(
            jti=jti,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(exp_timestamp, tz=UTC),
            fp=_fingerprint(new_token),
            revoked=False,
        )

        await token_repo.save(session=session, token=store_token)

        return new_token

    @staticmethod
    async def decrypt(session: AsyncSession, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.security.jwt_public_key,
                algorithms=["RS256"],
                options={"verify_exp": True},
            )

        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

        fp = _fingerprint(token)

        allowed = await token_repo.is_allowed(session=session, fp=fp)

        if not allowed:
            raise InvalidCredentialsError

        return payload

    async def issue_token(self, user: UserScheme, session: AsyncSession) -> str:
        token_payload = {"user_id": user.user_id}
        auth_token = await self.generate_token(
            session=session, user_id=user.user_id, payload=token_payload
        )

        return auth_token

    @staticmethod
    async def logout(jti: str, session: AsyncSession):
        jti_uuid = UUID(jti)
        await token_repo.revoke(session=session, jti=jti_uuid)


token_mgr: TokenManager = TokenManager()


def _fingerprint(token: str) -> str:
    unsigned = ".".join(token.split(".")[:2])
    return hashlib.sha256(unsigned.encode()).hexdigest()
