import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AksharAI - Multilingual AI Literacy Assistant"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aksharai_super_secret_jwt_key_2026_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./aksharai_dev.db"
    )
    
    # Sarvam AI Credentials
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_STT_ENDPOINT: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_TTS_ENDPOINT: str = "https://api.sarvam.ai/text-to-speech"
    SARVAM_TRANSLATE_ENDPOINT: str = "https://api.sarvam.ai/translate"

    @property
    def is_sarvam_configured(self) -> bool:
        key = (self.SARVAM_API_KEY or os.getenv("SARVAM_API_KEY", "")).strip().strip("'\"")
        return bool(key and key != "mock_sarvam_api_key")

    # SMTP Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "no-reply@aksharai.com")
    
    # Ollama Local LLM & AI Learning Path Generator Settings
    AI_LEARNING_ENGINE_ENABLED: bool = os.getenv("AI_LEARNING_ENGINE_ENABLED", "True").lower() in ("true", "1", "t")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    OLLAMA_TIMEOUT_SECONDS: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "15"))

    # Groq Cloud API (Free Tier — Open-Source LLM Inference)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_ENDPOINT: str = "https://api.groq.com/openai/v1/chat/completions"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto")  # "auto" | "groq" | "ollama" | "none"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
