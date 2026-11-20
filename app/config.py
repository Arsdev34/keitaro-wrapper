from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    keitaro_url: str
    keitaro_api_key: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
