import json
from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import (
    create_engine, Column, String, Integer,
    Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from ..config import settings

Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"

    username = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    public_repos = Column(Integer, default=0)
    indexed_repos = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    detected_languages = Column(Text, default="[]")
    status = Column(String(20), default="idle")
    last_indexed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def get_languages(self):
        try:
            return json.loads(self.detected_languages or "[]")
        except Exception:
            return []

    def set_languages(self, langs):
        self.detected_languages = json.dumps(langs)


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), index=True, nullable=False)
    name = Column(String(100), index=True, nullable=False)
    full_name = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    html_url = Column(String(255), nullable=False)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    language = Column(String(50), nullable=True)
    default_branch = Column(String(50), default="main")
    file_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    topics = Column(Text, default="[]")
    readme_content = Column(Text, nullable=True)
    last_pushed_at = Column(String(50), nullable=True)
    indexed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_repo_user_name", "username", "name", unique=True),
    )

    def get_topics(self):
        try:
            return json.loads(self.topics or "[]")
        except Exception:
            return []

    def set_topics(self, tops):
        self.topics = json.dumps(tops)


class IndexedFile(Base):
    __tablename__ = "indexed_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), index=True, nullable=False)
    repo_name = Column(String(100), index=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_extension = Column(String(20), nullable=False)
    language = Column(String(50), nullable=True)
    size = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    sha = Column(String(64), nullable=True)
    source_url = Column(String(500), nullable=False)

    __table_args__ = (
        Index("idx_file_user_repo", "username", "repo_name"),
    )


class IndexingJob(Base):
    __tablename__ = "indexing_jobs"

    username = Column(String(50), primary_key=True, index=True)
    status = Column(String(20), default="idle")
    progress_pct = Column(Integer, default=0)
    current_step = Column(String(100), default="Waiting to start")
    step_detail = Column(Text, default="")
    error_message = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))



engine = create_engine(
    f"sqlite:///{settings.SQLITE_DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
