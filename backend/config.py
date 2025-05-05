from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


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


class ApiPrefixConfig(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


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

    BaseSettings.model_config = ConfigDict(extra="ignore")


settings = Settings()
