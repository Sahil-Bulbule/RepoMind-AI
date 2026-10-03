from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from pathlib import PurePosixPath
from sqlalchemy.orm import Session
from ..config import settings
from ..models.database import get_db, Profile, Repository, IndexedFile, IndexingJob
from ..schemas.schemas import (
    AnalyzeRequest, StatusResponse, ProfileResponse,
    RepoResponse, RepoDetailResponse, FileInfo
)
from ..utils.file_filters import validate_github_username
from ..utils.rate_limiter import analyze_rate_limiter, global_rate_limiter
from ..services.indexing_service import indexing_service

router = APIRouter(prefix="/api/github", tags=["GitHub"])


def _build_repository_questions(repository: Repository, indexed_files: list[IndexedFile]) -> list[str]:
    paths = [item.file_path for item in indexed_files]
    readme = repository.readme_content or ""
    headings = [
        line.lstrip("# ").strip()
        for line in readme.splitlines()
        if line.startswith("#") and line.lstrip("# ").strip()
    ]
    file_stems = [PurePosixPath(path).name for path in paths if PurePosixPath(path).name.lower() != "readme.md"]
    folder_names = sorted({PurePosixPath(path).parent.name for path in paths if PurePosixPath(path).parent.name not in ("", ".")})
    primary_language = repository.language or next(
        (item.language for item in indexed_files if item.language),
        "the detected source languages",
    )

    questions = [
        f"What problem does {repository.name} solve, based on its README and description?",
        f"How is {primary_language} used across the indexed files in {repository.name}?",
    ]
    if file_stems:
        questions.append(f"What is the role of {file_stems[0]} in {repository.name}?")
    if len(file_stems) > 1:
        questions.append(f"How do {file_stems[0]} and {file_stems[1]} work together?")
    if headings:
        questions.append(f"What does the README say about {headings[0]}?")
    if folder_names:
        questions.append(f"How is the {folder_names[0]} directory organized?")
    if len(questions) < 4:
        questions.extend([
            f"Which indexed files best explain the main flow of {repository.name}?",
            f"What evidence in {repository.name} describes its architecture?",
        ])
    return list(dict.fromkeys(questions))[:6]

@router.post("/analyze", response_model=StatusResponse)
async def analyze_github_user(
    request: Request,
    body: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Initiates asynchronous indexing for a public GitHub user profile.
    """

    analyze_rate_limiter.check_request(request, custom_limit=15)

    username = body.username.strip()
    if not validate_github_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GitHub username: '{username}'. GitHub usernames must be 1-39 alphanumeric characters."
        )

    canon_user = username.lower()


    active_job = db.query(IndexingJob).filter(
        IndexingJob.username == canon_user,
        IndexingJob.status == "processing"
    ).first()

    if active_job:
        return StatusResponse(
            username=canon_user,
            status=active_job.status,
            progress_pct=active_job.progress_pct,
            current_step=active_job.current_step,
            step_detail=active_job.step_detail,
            error_message=(
                "Indexing failed. Check the server logs or verify the GitHub configuration."
                if active_job.status == "error"
                else None
            )
        )


    background_tasks.add_task(
        indexing_service.run_indexing_pipeline,
        username=canon_user,
        force_refresh=body.force_refresh
    )

    return StatusResponse(
        username=canon_user,
        status="processing",
        progress_pct=5,
        current_step="Starting analysis",
        step_detail=f"Connecting to GitHub API for @{username}..."
    )

@router.post("/refresh/{username}", response_model=StatusResponse)
async def refresh_github_data(
    username: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Forces cache invalidation and re-indexes the user's GitHub data.
    """
    analyze_rate_limiter.check_request(request, custom_limit=10)
    if not validate_github_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GitHub username format."
        )

    canon_user = username.lower()
    background_tasks.add_task(
        indexing_service.run_indexing_pipeline,
        username=canon_user,
        force_refresh=True
    )

    return StatusResponse(
        username=canon_user,
        status="processing",
        progress_pct=5,
        current_step="Refreshing knowledge base",
        step_detail="Invalidating existing cache and re-fetching repositories..."
    )

@router.get("/status/{username}", response_model=StatusResponse)
async def get_indexing_status(
    username: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Polls the progress status of a running or completed indexing job.
    """
    global_rate_limiter.check_request(request, custom_limit=120)
    canon_user = username.strip().lower()
    job = db.query(IndexingJob).filter(IndexingJob.username == canon_user).first()

    if not job:

        profile = db.query(Profile).filter(Profile.username == canon_user).first()
        if profile and profile.status == "completed":
            return StatusResponse(
                username=canon_user,
                status="completed",
                progress_pct=100,
                current_step="Knowledge base ready",
                step_detail="Profile already indexed."
            )
        return StatusResponse(
            username=canon_user,
            status="idle",
            progress_pct=0,
            current_step="Not started",
            step_detail="Profile has not been analyzed yet."
        )

    return StatusResponse(
        username=canon_user,
        status=job.status,
        progress_pct=job.progress_pct,
        current_step=job.current_step,
        step_detail=job.step_detail,
        error_message=(
            "Indexing failed. Check the server logs or verify the GitHub configuration."
            if job.status == "error"
            else None
        )
    )

@router.get("/profile/{username}", response_model=ProfileResponse)
async def get_user_profile(
    username: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Retrieve indexed profile information, statistics, and detected technologies.
    """
    global_rate_limiter.check_request(request)
    canon_user = username.strip().lower()
    profile = db.query(Profile).filter(Profile.username == canon_user).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '@{username}' has not been indexed yet."
        )

    return ProfileResponse(
        username=profile.username,
        name=profile.name,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        public_repos=profile.public_repos,
        indexed_repos=profile.indexed_repos,
        total_files=profile.total_files,
        total_chunks=profile.total_chunks,
        detected_languages=profile.get_languages(),
        status=profile.status,
        last_indexed_at=profile.last_indexed_at
    )

@router.get("/repositories/{username}", response_model=list[RepoResponse])
async def get_user_repositories(
    username: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get all indexed repositories for a given user.
    """
    global_rate_limiter.check_request(request)
    canon_user = username.strip().lower()
    repos = db.query(Repository).filter(Repository.username == canon_user).order_by(Repository.stars.desc()).all()

    return [
        RepoResponse(
            id=r.id,
            name=r.name,
            full_name=r.full_name,
            description=r.description,
            html_url=r.html_url,
            stars=r.stars,
            forks=r.forks,
            language=r.language,
            default_branch=r.default_branch,
            file_count=r.file_count,
            chunk_count=r.chunk_count,
            topics=r.get_topics(),
            has_readme=bool(r.readme_content),
            indexed_at=r.indexed_at
        )
        for r in repos
    ]

@router.get("/repository/{username}/{repo_name}", response_model=RepoDetailResponse)
async def get_repository_detail(
    username: str,
    repo_name: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get full repository details, README markdown, and indexed file tree.
    """
    global_rate_limiter.check_request(request)
    canon_user = username.strip().lower()
    repo = db.query(Repository).filter(
        Repository.username == canon_user,
        Repository.name == repo_name
    ).first()

    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repo_name}' for @{username} not found in database."
        )

    files = db.query(IndexedFile).filter(
        IndexedFile.username == canon_user,
        IndexedFile.repo_name == repo_name
    ).order_by(IndexedFile.file_path).all()

    repo_model = RepoResponse(
        id=repo.id,
        name=repo.name,
        full_name=repo.full_name,
        description=repo.description,
        html_url=repo.html_url,
        stars=repo.stars,
        forks=repo.forks,
        language=repo.language,
        default_branch=repo.default_branch,
        file_count=repo.file_count,
        chunk_count=repo.chunk_count,
        topics=repo.get_topics(),
        has_readme=bool(repo.readme_content),
        indexed_at=repo.indexed_at
    )

    important_files = [
        FileInfo(
            file_path=f.file_path,
            language=f.language,
            size=f.size,
            chunk_count=f.chunk_count,
            source_url=f.source_url
        )
        for f in files
    ]

    return RepoDetailResponse(
        repo=repo_model,
        readme_content=repo.readme_content,
        important_files=important_files
    )


@router.get("/repository/{username}/id/{repository_id}/suggestions")
async def get_repository_suggestions(
    username: str,
    repository_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    global_rate_limiter.check_request(request)
    canon_user = username.strip().lower()
    repository = db.query(Repository).filter(
        Repository.username == canon_user,
        Repository.id == repository_id,
    ).first()
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found for this GitHub profile.",
        )

    indexed_files = db.query(IndexedFile).filter(
        IndexedFile.username == canon_user,
        IndexedFile.repo_name == repository.name,
    ).order_by(IndexedFile.file_path).all()
    return {"questions": _build_repository_questions(repository, indexed_files)}
