import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "BenefitBridge AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    WORKSPACE_DIR: Path = BASE_DIR.parent
    
    # CSV Path resolution: check workspace schemes.csv, local data/schemes.csv, etc.
    SCHEMES_CSV_PATH: str = str(WORKSPACE_DIR / "schemes.csv")
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    
    # AI / Retrieval
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Search & Recommendation Parameters
    TOP_K_SEMANTIC: int = 40
    TOP_K_RECOMMENDATIONS: int = 10
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_valid_csv_path(self) -> Path:
        """Find the existing schemes CSV file across expected locations."""
        candidates = [
            Path(self.SCHEMES_CSV_PATH),
            self.WORKSPACE_DIR / "schemes.csv",
            self.WORKSPACE_DIR / "Schemes.csv",
            self.BASE_DIR / "data" / "schemes.csv",
            self.BASE_DIR / "data" / "Schemes.csv",
            self.BASE_DIR / "schemes.csv",
            Path("schemes.csv"),
            Path("Schemes.csv"),
            Path("E:/AI/schemes.csv"),
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c.resolve()
        raise FileNotFoundError(
            f"schemes.csv could not be found. Checked candidates: {[str(c) for c in candidates]}"
        )

settings = Settings()
