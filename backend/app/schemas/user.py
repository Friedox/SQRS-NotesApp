from pydantic import BaseModel, EmailStr, Field, SecretStr


class UserCredentialsScheme(BaseModel):
    email: EmailStr
    password: SecretStr

    name: str | None = None


class UserCreateScheme(BaseModel):
    email: str
    password_hash: str = Field(exclude=True)

    name: str | None = None


class UserScheme(UserCreateScheme):
    user_id: int
