from pydantic_settings import BaseSettings  # <-- CORRETO para Pydantic v2
from urllib.parse import quote_plus

class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "agrochip123@!#"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "py-bd"

    @property
    def DATABASE_URL(self):
        password_escaped = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{password_escaped}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()