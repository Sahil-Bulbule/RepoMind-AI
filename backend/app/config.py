import os
from pathlib import Path
from typing import List, Set
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):

    APP_NAME: str = "Ask My GitHub API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    

    GITHUB_TOKEN: str = Field(default="", description="Personal Access Token for GitHub")
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_RAW_BASE: str = "https://raw.githubusercontent.com"
    

    GROQ_API_KEY: str = Field(default="", description="Groq API key")
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    

    EMBEDDING_PROVIDER: str = "chroma_default"
    

    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "data" / "chroma_db")
    SQLITE_DB_PATH: str = str(BASE_DIR / "data" / "ask_my_github.db")
    

    MAX_FILES_PER_REPO: int = 50
    MAX_FILE_SIZE_BYTES: int = 102400
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    

    ALLOWED_EXTENSIONS: Set[str] = {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".html", ".css", ".java", ".c", ".cpp",
        ".h", ".hpp", ".md", ".json", ".yaml",
        ".yml", ".txt", ".go", ".rs", ".sql", ".sh"
    }
    

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    RATE_LIMIT_PER_MINUTE: int = 60
    

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def cors_origin_list(self) -> List[str]:
        if not self.CORS_ORIGINS or self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()


os.makedirs(Path(settings.SQLITE_DB_PATH).parent, exist_ok=True)
os.makedirs(Path(settings.CHROMA_PERSIST_DIRECTORY), exist_ok=True)
