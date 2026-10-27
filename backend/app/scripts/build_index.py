import sys
from app.data.csv_loader import loader
from app.retrieval.vector_store import vector_store
from app.core.logging_config import logger

def main():
    print("=" * 60)
    print(" BenefitBridge AI — SentenceTransformers Vector Indexer")
    print("=" * 60)
    schemes = loader.load_schemes()
    print(f"Loaded {len(schemes)} schemes from CSV.")
    print("Generating embeddings and building ChromaDB persistent collection...")
    res = vector_store.build_index(schemes, batch_size=200)
    print("Vector indexing finished!")
    print(f"Status: {res['status']}")
    print(f"Indexed Count: {res['indexed_count']}")
    print(f"Persist Directory: {res['persist_dir']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
