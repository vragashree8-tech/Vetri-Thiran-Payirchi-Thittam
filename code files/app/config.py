from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    gemini_api_key: str | None = None
    hf_token: str | None = None
    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-2.5-flash"
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    image_provider: str = "auto"  # auto, huggingface, demo
    max_prompt_chars: int = 1200
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
