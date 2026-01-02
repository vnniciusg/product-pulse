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


class AppConfig(BaseModel):
    SCRAPER: ScraperAPIConfig = Field(default_factory=ScraperAPIConfig)


app_config = AppConfig()
