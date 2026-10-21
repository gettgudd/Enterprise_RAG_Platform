from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_name: str = "enterprise-rag-platform"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    api_port: int = 8000

    # Vector Database (ChromaDB primary, Qdrant supported)
    vector_db_type: str = "chromadb"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "enterprise_documents"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "enterprise_chunks"

    # PostgreSQL Application DB (users, permissions, chat history, feedback)
    postgres_user: str = "rag"
    postgres_password: str = "change_me"
    postgres_db: str = "rag"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis Cache & Task Queue
    redis_url: str = "redis://localhost:6379/0"

    # File Storage (AWS S3 & Local Storage fallback for PDF/Word/Excel/PPT)
    s3_bucket_name: str = "enterprise-rag-documents"
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_endpoint_url: str | None = None
    local_storage_dir: str = "data/storage"

    # Embeddings & Models
    embedding_provider: str = "local"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # LLM Providers
    llm_provider: str = ""
    llm_api_key: str = ""

    # Auth & Security
    jwt_secret: str = "change_me_super_secret_jwt_key_32_bytes_long"
    jwt_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"

    # Local Directory Paths
    data_dir: str = "data"
    model_cache_dir: str = "models_cache"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
