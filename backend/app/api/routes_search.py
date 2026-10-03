from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..models.database import get_db, Profile, Repository
from ..schemas.schemas import (
    RepositorySearchResult,
    SearchEvidenceFile,
    SearchRequest,
    SearchResponse,
)
from ..utils.file_filters import validate_github_username
from ..utils.rate_limiter import global_rate_limiter
from ..rag.vector_store import vector_store

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])

@router.post("", response_model=SearchResponse)
async def search_repositories(
    request: Request,
    body: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Find relevant repositories and return indexed files as supporting evidence.
    """
    global_rate_limiter.check_request(request, custom_limit=40)

    username = body.github_username.strip()
    if not validate_github_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GitHub username."
        )

    if not body.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty."
        )

    canon_user = username.lower()

    profile = db.query(Profile).filter(Profile.username == canon_user).first()
    if not profile or profile.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GitHub profile @{username} has not been indexed yet."
        )

    raw_results = vector_store.lexical_search(
        username=canon_user,
        query_text=body.query,
        repository_filter=body.repository_filter,
        top_k=5000
    )

    repositories = db.query(Repository).filter(Repository.username == canon_user).all()
    repositories_by_name = {repository.name.casefold(): repository for repository in repositories}
    grouped_results = {}
    for r in raw_results:
        meta = r["metadata"]
        repository_name = meta.get("repository_name", "")
        repository = repositories_by_name.get(repository_name.casefold())
        if not repository:
            continue

        score = r.get("score", 0.0)
        file_path = meta.get("file_path", "Unknown")
        result = grouped_results.setdefault(
            repository.name.casefold(),
            {
                "repository": repository,
                "score": score,
                "files": {},
            },
        )
        result["score"] = max(result["score"], score)
        evidence = result["files"].get(file_path)
        if evidence is None or score > evidence["score"]:
            result["files"][file_path] = {
                "file_path": file_path,
                "source_url": meta.get("source_url", ""),
                "language": meta.get("language", "Code"),
                "score": score,
            }

    ranked_results = sorted(
        grouped_results.values(),
        key=lambda result: (result["score"], len(result["files"])),
        reverse=True,
    )[:min(body.limit, 3)]
    items = [
        RepositorySearchResult(
            repository_name=result["repository"].name,
            repository_full_name=(
                result["repository"].full_name
                or f"{result['repository'].username}/{result['repository'].name}"
            ),
            description=result["repository"].description,
            html_url=result["repository"].html_url,
            language=result["repository"].language,
            score=result["score"],
            matching_files=len(result["files"]),
            evidence_files=[
                SearchEvidenceFile(**evidence)
                for evidence in sorted(
                    result["files"].values(),
                    key=lambda item: item["score"],
                    reverse=True,
                )[:3]
            ],
        )
        for result in ranked_results
    ]

    return SearchResponse(
        query=body.query,
        github_username=canon_user,
        total_results=len(items),
        results=items
    )
