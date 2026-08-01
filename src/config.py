from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get path to root project directory (one folder up from src/)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str


    # Instructing pydantic-setting to load our variables from .env
    model_config = SettingsConfigDict(
        env_file = ENV_FILE_PATH,
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

    # Method that puts together the database url
    def database_url(self) -> str:
        """
        Put together the SQLAlchemy connection string.
        Format:postgresql+psycopg://user:password@host:port/dbname
        """

        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

# Creating an instance of the Settings class
settings = Settings()

print(BASE_DIR)

