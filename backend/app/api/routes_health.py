from fastapi import APIRouter
from ..config import settings
from ..schemas.schemas import HealthResponse
from ..rag.vector_store import vector_store

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health status endpoint checking DB, Chroma vector store, and API keys.
    """
    try:
        vec_count = vector_store.count()
        chroma_stat = f"connected ({vec_count} vectors)"
    except Exception:
        chroma_stat = "unavailable"

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        chroma_status=chroma_stat,
        groq_configured=bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip()),
        github_token_configured=bool(settings.GITHUB_TOKEN and settings.GITHUB_TOKEN.strip()),
        embedding_provider=settings.EMBEDDING_PROVIDER
    )
