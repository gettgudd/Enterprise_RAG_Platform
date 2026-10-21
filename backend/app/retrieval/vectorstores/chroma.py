"""ChromaDB vector store client wrapper per Architecture Plan."""

from typing import Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ChromaVectorStore:
    """ChromaDB client managing document embeddings, chunks, and metadata filtering."""

    def __init__(self) -> None:
        if settings.app_env == "test":
            # In-memory client for testing
            self.client = chromadb.Client()
        elif settings.chroma_host in ("localhost", "127.0.0.1") and settings.chroma_port == 8000:
            # Connect via HTTP or persistent local client
            try:
                self.client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
            except Exception:
                self.client = chromadb.PersistentClient(path="data/chroma")
        else:
            self.client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )

        self.collection_name = settings.chroma_collection

    def get_or_create_collection(self) -> Any:
        """Retrieve or initialize the primary document collection."""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Enterprise documents with RBAC access levels"},
        )

    def add_chunks(
        self,
        chunk_ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Store chunk embeddings, text content, and metadata in ChromaDB."""
        collection = self.get_or_create_collection()
        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 5,
        where_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform semantic search with optional RBAC metadata filtering."""
        collection = self.get_or_create_collection()
        return collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where_filter,
        )
