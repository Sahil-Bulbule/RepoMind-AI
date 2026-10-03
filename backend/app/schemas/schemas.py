from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field





class AnalyzeRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=39, description="Target GitHub username")
    force_refresh: bool = Field(default=False, description="Whether to invalidate cache and re-index")

class StatusResponse(BaseModel):
    username: str
    status: str
    progress_pct: int
    current_step: str
    step_detail: str
    error_message: Optional[str] = None

class ProfileResponse(BaseModel):
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int
    indexed_repos: int
    total_files: int
    total_chunks: int
    detected_languages: List[str]
    status: str
    last_indexed_at: Optional[datetime] = None

class RepoResponse(BaseModel):
    id: int
    name: str
    full_name: Optional[str] = None
    description: Optional[str] = None
    html_url: str
    stars: int
    forks: int
    language: Optional[str] = None
    default_branch: str
    file_count: int
    chunk_count: int
    topics: List[str]
    has_readme: bool
    indexed_at: Optional[datetime] = None

class FileInfo(BaseModel):
    file_path: str
    language: Optional[str] = None
    size: int
    chunk_count: int
    source_url: str

class RepoDetailResponse(BaseModel):
    repo: RepoResponse
    readme_content: Optional[str] = None
    important_files: List[FileInfo]





class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    github_username: str = Field(..., min_length=1, max_length=39)
    message: str = Field(default="", max_length=2000)
    question: Optional[str] = Field(default=None, max_length=2000)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    repository_filter: Optional[str] = None
    repository_id: Optional[int] = None
    repository_name: Optional[str] = None
    repository_full_name: Optional[str] = None
    repository_url: Optional[str] = None

class SourceCitation(BaseModel):
    repository_name: str
    repository_full_name: Optional[str] = None
    file_path: str
    source_url: str
    language: str
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    used_repository_filter: Optional[str] = None





class SearchRequest(BaseModel):
    github_username: str = Field(..., min_length=1, max_length=39)
    query: str = Field(..., min_length=1, max_length=500)
    repository_filter: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)

class SearchEvidenceFile(BaseModel):
    file_path: str
    source_url: str
    language: str
    score: float

class RepositorySearchResult(BaseModel):
    repository_name: str
    repository_full_name: Optional[str] = None
    description: Optional[str] = None
    html_url: str
    language: Optional[str] = None
    score: float
    matching_files: int
    evidence_files: List[SearchEvidenceFile]

class SearchResponse(BaseModel):
    query: str
    github_username: str
    total_results: int
    results: List[RepositorySearchResult]





class HealthResponse(BaseModel):
    status: str
    version: str
    chroma_status: str
    groq_configured: bool
    github_token_configured: bool
    embedding_provider: str
