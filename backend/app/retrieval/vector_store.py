import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.scheme import Scheme
from app.retrieval.embeddings import embedding_service

COLLECTION_NAME = "welfare_schemes"
FINGERPRINT_FILE = "dataset_fingerprint.json"

def compute_file_fingerprint(filepath: Path) -> Dict[str, Any]:
    """Calculate file size and MD5 hash to track dataset changes."""
    stat = filepath.stat()
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        # Read in 64kb chunks
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return {
        "file_size": stat.st_size,
        "mtime": stat.st_mtime,
        "md5": hasher.hexdigest(),
        "path": str(filepath.resolve())
    }

class LocalSentenceTransformerEmbedding(chromadb.EmbeddingFunction):
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        return embedding_service.embed_texts(input)

local_embedding_function = LocalSentenceTransformerEmbedding()

class ChromaVectorStore:
    _instance: Optional["ChromaVectorStore"] = None

    def __init__(self):
        self.persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self._collection = None

    @classmethod
    def get_instance(cls) -> "ChromaVectorStore":
        if cls._instance is None:
            cls._instance = ChromaVectorStore()
        return cls._instance

    def get_collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=local_embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def count(self) -> int:
        try:
            return self.get_collection().count()
        except Exception:
            return 0

    def is_stale(self) -> Tuple[bool, str]:
        """Check if index is missing or out of sync with current CSV."""
        fingerprint_path = self.persist_dir / FINGERPRINT_FILE
        if not fingerprint_path.exists():
            return True, "No fingerprint found; index needs to be initialized."
        
        try:
            csv_path = settings.get_valid_csv_path()
            stat = csv_path.stat()
            with open(fingerprint_path, "r", encoding="utf-8") as f:
                saved_fp = json.load(f)
            if stat.st_size != saved_fp.get("file_size"):
                return True, "CSV file has been modified since last indexing."
            if self.count() == 0:
                return True, "ChromaDB collection is empty."
            return False, "Index is fresh and in sync with CSV."
        except Exception as e:
            return True, f"Error validating index freshness: {e}"

    def build_index(self, schemes: List[Scheme], batch_size: int = 250) -> Dict[str, Any]:
        """Indexes schemes into ChromaDB with embeddings and metadata."""
        logger.info(f"Starting vector index build for {len(schemes)} schemes...")
        collection = self.get_collection()

        # Delete existing entries if any to prevent duplicates on rebuild
        existing_count = collection.count()
        if existing_count > 0:
            logger.info(f"Clearing existing {existing_count} records from collection...")
            self.client.delete_collection(name=COLLECTION_NAME)
            self._collection = self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=local_embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            collection = self._collection

        total = len(schemes)
        indexed_count = 0

        for i in range(0, total, batch_size):
            batch = schemes[i:i + batch_size]
            ids = [s.id for s in batch]
            documents = [s.searchable_text for s in batch]
            metadatas = [
                {
                    "name": s.name[:250],
                    "level": s.level,
                    "state": s.state or "All India",
                    "benefit_type": s.benefit_type,
                    "categories": ", ".join(s.categories[:3]),
                    "min_age": s.parsed_criteria.min_age or -1,
                    "max_age": s.parsed_criteria.max_age or -1,
                    "max_income": s.parsed_criteria.max_income or -1.0,
                    "is_central": s.parsed_criteria.is_central,
                }
                for s in batch
            ]
            embeddings = embedding_service.embed_texts(documents, batch_size=batch_size)
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            indexed_count += len(batch)
            logger.info(f"Indexed {indexed_count}/{total} schemes...")

        # Save fingerprint
        try:
            csv_path = settings.get_valid_csv_path()
            fp = compute_file_fingerprint(csv_path)
            fp["indexed_count"] = indexed_count
            with open(self.persist_dir / FINGERPRINT_FILE, "w", encoding="utf-8") as f:
                json.dump(fp, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not write dataset fingerprint: {e}")

        logger.info(f"Vector index build completed: {indexed_count} items stored.")
        return {
            "status": "success",
            "indexed_count": indexed_count,
            "persist_dir": str(self.persist_dir)
        }

    def query(self, query_text: str, n_results: int = 40) -> List[Tuple[str, float]]:
        """
        Query nearest schemes. Returns list of (scheme_id, similarity_score).
        Cosine distance in ChromaDB is in [0, 2], where 0 is identical.
        Similarity score = 1.0 - (distance / 2.0)
        """
        if self.count() == 0:
            logger.warning("Vector store is empty! Query returning empty list.")
            return []

        query_emb = embedding_service.embed_query(query_text)
        collection = self.get_collection()
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=min(n_results, self.count()),
            include=["distances"]
        )

        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        pairs = []
        for sid, dist in zip(ids, distances):
            sim = max(0.0, min(1.0, 1.0 - (float(dist) / 2.0)))
            pairs.append((sid, sim))
        return pairs

vector_store = ChromaVectorStore.get_instance()
