from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")

    PROJECT_NAME: str = "PolicyDiff"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./policydiff.db"  # Defaults to SQLite for local development, easily overridden with PostgreSQL
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days


settings = Settings()
