
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    APP_NAME: str = "Senai AutoHub"
    SECRET_KEY: str = "change-me-secret"
    CSRF_SECRET: str = "change-me-csrf"
    DATABASE_URL: str = "sqlite:///./senai_autohub.db"
    SESSION_COOKIE_NAME: str = "senai_session"
    SESSION_EXPIRE_MINUTES: int = 60

    # Admin padrão (trocar em produção)
    ADMIN_EMAIL: str = "admin@senai.autohub"
    ADMIN_PASSWORD: str = "Admin123!"

    class Config:
        env_file = ".env"


settings = Settings()
