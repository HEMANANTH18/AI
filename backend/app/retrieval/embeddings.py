import os
from typing import List, Optional

# Enforce offline mode once weights are cached to prevent network retry pauses
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging_config import logger

class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = EmbeddingService()
        return cls._instance

    def get_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Initializing embedding model: {settings.EMBEDDING_MODEL}")
            try:
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL, local_files_only=True)
            except Exception:
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully.")
        return self._model

    def embed_texts(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        model = self.get_model()
        embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        model = self.get_model()
        embedding = model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

embedding_service = EmbeddingService.get_instance()
