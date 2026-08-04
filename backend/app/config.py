from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_host: str = "http://localhost:11434"
    ollama_generation_model: str = "qwen2.5:7b-instruct-q4_K_M"
    ollama_embedding_model: str = "nomic-embed-text"

    database_path: str = "./data/skilldrill.db"

    generation_batch_size: int = 75
    generation_low_watermark: int = 15
    generation_max_retries: int = 3
    dedup_similarity_threshold: float = 0.9

    app_pin: str = "changeme"
    session_secret: str = "changeme-session-secret"

    scenario_pass_threshold: float = 70.0
    cors_origin: str = "http://localhost:5173"

    weak_topic_threshold: float = 70.0

    top_up_enabled: bool = True
    top_up_interval_minutes: int = 30
    top_up_initial_delay_seconds: int = 15


settings = Settings()
