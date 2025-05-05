from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    status_prefix: str = "/status"


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

    BaseSettings.model_config = ConfigDict(extra="ignore")


settings = Settings()
