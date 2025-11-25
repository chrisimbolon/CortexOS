# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    EMBEDDING_SERVICE_URL: str = Field(..., env="EMBEDDING_SERVICE_URL")
    VECTOR_DB_PATH: str = Field("vector_store", env="VECTOR_DB_PATH")

    CHUNK_SIZE: int = Field(800, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(100, env="CHUNK_OVERLAP")

    DATABASE_URL: str = "postgresql+psycopg://postgres:password@localhost:5432/cortex_os"


    class Config:
        env_file = ".env"


settings = Settings()
