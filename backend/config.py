from typing import Final

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

ONE_DAY_IN_SECONDS: Final[int] = 24 * 60 * 60


class DatabaseConfig(BaseModel):
    db_url: str
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 50

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    model_config = ConfigDict(extra="ignore")


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    status_prefix: str = "/status"
    auth_prefix: str = "/auth"
    notes_prefix: str = "/notes"
    translation_prefix: str = "/translation"


class ApiPrefixConfig(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class SecurityConfig(BaseModel):
    jwt_private_key: SecretStr
    jwt_public_key: str
    jwt_expires_in: int = ONE_DAY_IN_SECONDS
    jwt_issuer_name: str = "notes_app"


class RedisConfig(BaseModel):
    url: str


class TranslationConfig(BaseModel):
    api_key: SecretStr
    cache_ttl: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="CONFIG__",
        env_file=".env",
    )
    run: RunConfig
    api: ApiPrefixConfig = ApiPrefixConfig()
    database: DatabaseConfig
    security: SecurityConfig
    redis: RedisConfig
    translation: TranslationConfig

    BaseSettings.model_config = ConfigDict(extra="ignore")


settings = Settings()
