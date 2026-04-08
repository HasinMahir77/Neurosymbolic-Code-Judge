from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    sandbox_timeout_seconds: int = 60
    max_refinement_attempts: int = 3
    thinking_budget: int = 0  # 0 = fast-first with thinking escalation on error; -1 = always full thinking
