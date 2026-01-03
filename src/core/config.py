from typing import ClassVar, Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperAPIConfig(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8",
        env_prefix="SCRAPERAPI_",
    )

    KEY: SecretStr
    OUTPUT_FORMAT: Literal["markdown"] | None = Field(default="markdown")
    COUNTRY_CODE: str = Field(default="br")


class ServerConfig(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8",
        env_prefix="SERVER_",
    )

    TITLE: str = Field(default="Product Pulse Agent API")
    DESCRIPTION: str = Field(default="Streaming API for Product Pulse Agent")
    VERSION: str = Field(default="1.0.0")
    FRONTEND_URL: str = Field(default="http://")
    TOKEN: SecretStr


class AppConfig(BaseModel):
    SCRAPER: ScraperAPIConfig = Field(default_factory=ScraperAPIConfig)
    SERVER: ServerConfig = Field(default_factory=ServerConfig)


app_config = AppConfig()
