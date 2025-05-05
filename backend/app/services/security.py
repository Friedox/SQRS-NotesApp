import time

import jwt

from app.schemas.user import UserScheme
from config import settings


class TokenManager:
    @staticmethod
    async def generate_token(payload: dict, expires_in: int = None) -> str:
        payload["exp"] = int(time.time()) + (
            expires_in or settings.security.jwt_expires_in
        )
        payload["iss"] = settings.security.jwt_issuer_name
        payload["type"] = "access"

        try:
            return jwt.encode(
                payload,
                settings.security.jwt_private_key.get_secret_value(),
                algorithm="RS256",
            )

        except Exception as e:
            raise ValueError(f"Failed to generate token: {str(e)}")

    @staticmethod
    async def decrypt(token: str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.security.jwt_public_key, algorithms=["RS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def issue_token(self, user: UserScheme) -> str:
        token_payload = {
            "user_id": user.user_id,
        }

        auth_token = await self.generate_token(payload=token_payload)

        return auth_token


token_mgr: TokenManager = TokenManager()
