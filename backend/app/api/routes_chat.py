from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..models.database import get_db, IndexedFile, Profile, Repository
from ..schemas.schemas import ChatRequest, ChatResponse
from ..utils.file_filters import validate_github_username
from ..utils.rate_limiter import chat_rate_limiter
from ..rag.retriever import retriever
from ..rag.generator import generator
from ..rag.vector_store import vector_store

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])


def _is_profile_overview_request(message: str) -> bool:
    normalized = " ".join(message.lower().split())
    if any(
        phrase in normalized
        for phrase in (
            "summarize",
            "summary",
            "overview",
            "main projects",
            "what projects",
            "projects do you have",
            "github profile",
            "developer profile",
            "technology stack",
            "tech stack",
            "technologies across",
            "technology across",
            "language breakdown",
            "programming languages",
            "across all projects",
            "all projects",
            "all repositories",
            "across repositories",
            "across my repos",
            "repositories use",
            "projects use",
        )
    ):
        return True

    metadata_terms = {
        "profile",
        "project",
        "projects",
        "repo",
        "repos",
        "repository",
        "repositories",
        "language",
        "languages",
        "technology",
        "technologies",
        "stack",
        "framework",
        "frameworks",
    }
    return bool(metadata_terms.intersection(normalized.split()))


def _format_profile_overview(profile: Profile, repositories: list[Repository]) -> str:
    lines = [
        "=== INDEXED GITHUB PROFILE AND REPOSITORY METADATA ===",
        f"GitHub username: @{profile.username}",
    ]
    if profile.name:
        lines.append(f"Name: {profile.name}")
    if profile.bio:
        lines.append(f"Public profile bio: {profile.bio}")
    lines.extend(
        [
            f"Public repositories: {profile.public_repos or 0}",
            f"Repositories indexed: {profile.indexed_repos or 0}",
            f"Files indexed: {profile.total_files or 0}",
            f"Detected languages: {', '.join(profile.get_languages()) or 'Not available'}",
            "Indexed repositories:",
        ]
    )

    for repository in repositories:
        details = []
        if repository.description:
            details.append(f"Description: {repository.description}")
        if repository.language:
            details.append(f"Language: {repository.language}")
        details.extend(
            [
                f"Stars: {repository.stars or 0}",
                f"Files indexed: {repository.file_count or 0}",
            ]
        )
        topics = repository.get_topics()
        if topics:
            details.append(f"Topics: {', '.join(topics)}")
        lines.append(f"- {repository.name} ({'; '.join(details)})")

    return "\n".join(lines)


def _format_repository_context(repository: Repository, indexed_files: list[IndexedFile]) -> str:
    lines = [
        f"=== SELECTED REPOSITORY METADATA: {repository.full_name or repository.name} ===",
    ]
    if repository.description:
        lines.append(f"Description: {repository.description}")
    if repository.language:
        lines.append(f"Primary language: {repository.language}")
    topics = repository.get_topics()
    if topics:
        lines.append(f"Topics: {', '.join(topics)}")
    lines.append(f"Indexed files: {repository.file_count or len(indexed_files)}")
    if indexed_files:
        lines.append("Indexed file paths:")
        lines.extend(f"- {file.file_path}" for file in indexed_files[:100])
    if repository.readme_content:
        lines.extend(["Repository README:", repository.readme_content.strip()[:8000]])
    return "\n".join(lines)


@router.post("", response_model=ChatResponse)
async def chat_with_github(
    request: Request,
    body: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    RAG-grounded conversational endpoint.
    Retrieves semantic repository chunks isolated strictly to the given GitHub user,
    constructs the anti-hallucination prompt, and generates an answer with source citations.
    """
    chat_rate_limiter.check_request(request, custom_limit=30)

    username = body.github_username.strip()
    if not validate_github_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GitHub username format."
        )

    message = (body.question or body.message).strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    canon_user = username.lower()


    profile = db.query(Profile).filter(Profile.username == canon_user).first()
    if not profile or profile.status not in {"indexing", "completed"}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GitHub profile @{username} has not been indexed yet. Please analyze the profile first."
        )

    requested_repo_name = body.repository_name or body.repository_filter
    requested_full_name = body.repository_full_name
    repository = None
    if body.repository_id is not None or requested_repo_name or requested_full_name or body.repository_url:
        repositories = db.query(Repository).filter(Repository.username == canon_user).all()
        for candidate in repositories:
            candidate_full_name = (candidate.full_name or f"{candidate.username}/{candidate.name}").casefold()
            if body.repository_id is not None and candidate.id != body.repository_id:
                continue
            if requested_repo_name and candidate.name.casefold() != requested_repo_name.strip().casefold():
                continue
            if requested_full_name and candidate_full_name != requested_full_name.strip().casefold():
                continue
            if body.repository_url and candidate.html_url.rstrip("/").casefold() != body.repository_url.strip().rstrip("/").casefold():
                continue
            repository = candidate
            break
        if not repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The selected repository does not belong to this indexed GitHub profile.",
            )

    repository_name = repository.name if repository else None
    repository_full_name = (
        (repository.full_name or f"{repository.username}/{repository.name}").lower()
        if repository else None
    )
    repository_id = repository.id if repository else None
    repository_url = repository.html_url if repository else None
    if repository:
        vector_store.ensure_repository_metadata(
            username=canon_user,
            repository_name=repository.name,
            repository_id=repository.id,
            repository_full_name=repository_full_name,
            repository_url=repository.html_url,
        )


    retrieved_chunks, citations = retriever.retrieve(
        username=canon_user,
        query=message,
        repository_filter=repository_name,
        repository_id=repository_id,
        repository_full_name=repository_full_name,
        repository_url=repository_url,
        conversation_history=body.conversation_history,
        top_k=10,
    )

    context_text = retriever.format_context_for_prompt(retrieved_chunks)
    if repository:
        indexed_files = (
            db.query(IndexedFile)
            .filter(
                IndexedFile.username == canon_user,
                IndexedFile.repo_name == repository.name,
            )
            .order_by(IndexedFile.file_path.asc())
            .limit(100)
            .all()
        )
        repository_context = _format_repository_context(repository, indexed_files)
        context_text = f"{repository_context}\n\n{context_text}"
    elif _is_profile_overview_request(message) or not retrieved_chunks:
        repository_query = db.query(Repository).filter(Repository.username == canon_user)
        repositories = repository_query.order_by(Repository.stars.desc(), Repository.name.asc()).all()
        profile_context = _format_profile_overview(profile, repositories)
        context_text = f"{profile_context}\n\n{context_text}"


    answer = await generator.generate_answer(
        username=username,
        question=message,
        context_text=context_text,
        conversation_history=body.conversation_history,
        repository_filter=repository.name if repository else None,
        repository_full_name=repository_full_name,
    )

    return ChatResponse(
        answer=answer,
        sources=citations,
        used_repository_filter=repository.name if repository else None
    )
