from datetime import UTC, datetime

from pydantic import UUID4, BaseModel, Field, SecretStr


class TokenScheme(BaseModel):
    jti: UUID4
    user_id: int
    expires_at: datetime
    fp: SecretStr

    revoked: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
