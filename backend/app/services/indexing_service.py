import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..config import settings
from ..models.database import SessionLocal, Profile, Repository, IndexedFile, IndexingJob
from ..services.github_service import GitHubService, GitHubAPIError
from ..rag.chunker import CodeTextChunker
from ..rag.vector_store import vector_store

logger = logging.getLogger("ask_my_github")

class IndexingService:
    def __init__(self):
        self.chunker = CodeTextChunker()
        self.github_service = GitHubService()

    async def _fetch_repository_sources(
        self,
        owner: str,
        repository: Dict[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        async def fetch_tree():
            async with semaphore:
                return await self.github_service.get_repository_tree(
                    owner,
                    repository["name"],
                    repository.get("default_branch") or "main",
                )

        async def fetch_readme():
            async with semaphore:
                return await self.github_service.get_readme(owner, repository["name"])

        return await asyncio.gather(fetch_tree(), fetch_readme())

    def _update_job_status(
        self,
        db: Session,
        username: str,
        status: str,
        progress_pct: int,
        current_step: str,
        step_detail: str = "",
        error_message: Optional[str] = None
    ):
        """Update or create job status record in database."""
        job = db.query(IndexingJob).filter(IndexingJob.username == username.lower()).first()
        if not job:
            job = IndexingJob(username=username.lower())
            db.add(job)

        job.status = status
        job.progress_pct = progress_pct
        job.current_step = current_step
        job.step_detail = step_detail
        job.error_message = error_message
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

    async def run_indexing_pipeline(self, username: str, force_refresh: bool = False):
        """
        Full asynchronous indexing pipeline for a GitHub user.
        """
        canon_user = username.strip().lower()
        db = SessionLocal()

        try:

            self._update_job_status(
                db, canon_user, "processing", 10,
                "Validating user", f"Searching GitHub for @{username}..."
            )


            profile_data = await self.github_service.get_user_profile(username)
            self._update_job_status(
                db, canon_user, "processing", 20,
                "GitHub profile found", f"Found @{profile_data['username']} ({profile_data['public_repos']} public repositories)"
            )


            repos = await self.github_service.get_user_repositories(username)
            repos = [repository for repository in repos if not repository.get("private", False)]


            if force_refresh:
                vector_store.delete_user_knowledge(canon_user)
                db.query(IndexedFile).filter(IndexedFile.username == canon_user).delete()
                db.query(Repository).filter(Repository.username == canon_user).delete()
                db.commit()


            profile = db.query(Profile).filter(Profile.username == canon_user).first()
            if not profile:
                profile = Profile(username=canon_user)
                db.add(profile)
            profile.name = profile_data["name"]
            profile.avatar_url = profile_data["avatar_url"]
            profile.bio = profile_data["bio"]
            profile.public_repos = profile_data["public_repos"]
            profile.indexed_repos = 0
            profile.total_files = 0
            profile.total_chunks = 0
            profile.status = "indexing"
            profile.set_languages(list(dict.fromkeys(
                repo.get("language") for repo in repos if repo.get("language")
            )))

            repo_names = {repo["name"] for repo in repos}
            existing_repositories = db.query(Repository).filter(
                Repository.username == canon_user,
            ).all()
            for existing_repository in existing_repositories:
                if existing_repository.name not in repo_names:
                    vector_store.delete_repository_knowledge(
                        canon_user,
                        existing_repository.name,
                    )

            for repo_data in repos:
                repo_name = repo_data["name"]
                repository = db.query(Repository).filter(
                    Repository.username == canon_user,
                    Repository.name == repo_name,
                ).first()
                if not repository:
                    repository = Repository(
                        username=canon_user,
                        name=repo_name,
                        file_count=0,
                        chunk_count=0,
                    )
                    db.add(repository)
                repository.full_name = repo_data.get("full_name")
                repository.description = repo_data.get("description")
                repository.html_url = repo_data["html_url"]
                repository.stars = repo_data.get("stargazers_count", 0)
                repository.forks = repo_data.get("forks_count", 0)
                repository.language = repo_data.get("language")
                repository.default_branch = repo_data.get("default_branch") or "main"
                repository.last_pushed_at = repo_data.get("pushed_at", "")
                repository.set_topics(repo_data.get("topics", []))

            if repo_names:
                db.query(Repository).filter(
                    Repository.username == canon_user,
                    Repository.name.notin_(repo_names),
                ).delete(synchronize_session=False)
                db.query(IndexedFile).filter(
                    IndexedFile.username == canon_user,
                    IndexedFile.repo_name.notin_(repo_names),
                ).delete(synchronize_session=False)
            else:
                db.query(Repository).filter(Repository.username == canon_user).delete()
                db.query(IndexedFile).filter(IndexedFile.username == canon_user).delete()

            db.commit()
            self._update_job_status(
                db, canon_user, "processing", 35,
                "Repositories discovered", f"Found {len(repos)} public repositories"
            )

            if not repos:
                profile.status = "completed"
                profile.last_indexed_at = datetime.now(timezone.utc)
                db.commit()
                self._update_job_status(
                    db, canon_user, "completed", 100,
                    "No public repositories found", "This GitHub user has no public repositories."
                )
                return


            all_chunks = []
            all_indexed_files = []
            processed_repos = []
            all_file_paths_for_tech = []
            repo_languages = []

            total_repos = len(repos)
            github_semaphore = asyncio.Semaphore(12)
            source_results = await asyncio.gather(*(
                self._fetch_repository_sources(
                    profile_data["username"],
                    repository,
                    github_semaphore,
                )
                for repository in repos
            ))

            for idx, r in enumerate(repos):
                repo_name = r["name"]
                repo_full_name = (r.get("full_name") or f"{profile_data['username']}/{repo_name}").lower()
                source_repo_id = str(r.get("id") or repo_full_name)
                default_branch = r.get("default_branch") or "main"
                repo_url = r["html_url"]
                last_pushed = r.get("pushed_at", "")
                main_lang = r.get("language") or "Code"
                if main_lang:
                    repo_languages.append(main_lang)

                step_pct = 35 + int(((idx + 1) / total_repos) * 30)
                self._update_job_status(
                    db, canon_user, "processing", step_pct,
                    "Collecting files", f"Scanning repository {idx+1}/{total_repos}: {repo_name}"
                )


                tree_items, readme_text = source_results[idx]

                candidate_files = [
                    item for item in tree_items
                    if item.get("type") == "blob" and self._is_candidate(item.get("path", ""))
                ][:settings.MAX_FILES_PER_REPO]

                repo_chunks = []
                repo_file_count = 0

                if readme_text:
                    rm_chunks = self.chunker.chunk_file(
                        username=canon_user,
                        repo_name=repo_name,
                        repo_url=repo_url,
                        file_path="README.md",
                        branch=default_branch,
                        content=readme_text,
                        repository_full_name=repo_full_name,
                        repository_id=source_repo_id,
                    )
                    repo_chunks.extend(rm_chunks)
                    repo_file_count += 1
                    all_file_paths_for_tech.append("README.md")

                eligible_files = []
                for f_item in candidate_files:
                    path = f_item.get("path")
                    if not path or path.lower() == "readme.md":
                        continue

                    size = f_item.get("size", 0)
                    if size and size > settings.MAX_FILE_SIZE_BYTES:
                        continue
                    eligible_files.append(f_item)

                async def fetch_candidate_file(file_item):
                    async with github_semaphore:
                        content = await self.github_service.fetch_file_content(
                            profile_data["username"],
                            repo_name,
                            default_branch,
                            file_item["path"],
                        )
                    return file_item, content

                fetched_files = await asyncio.gather(
                    *(fetch_candidate_file(item) for item in eligible_files)
                )

                for f_item, content in fetched_files:
                    path = f_item["path"]
                    size = f_item.get("size", 0)
                    if not content:
                        continue

                    file_chunks = self.chunker.chunk_file(
                        username=canon_user,
                        repo_name=repo_name,
                        repo_url=repo_url,
                        file_path=path,
                        branch=default_branch,
                        content=content,
                        repository_full_name=repo_full_name,
                        repository_id=source_repo_id,
                    )
                    if file_chunks:
                        repo_chunks.extend(file_chunks)
                        repo_file_count += 1
                        all_file_paths_for_tech.append(path)

                        all_indexed_files.append(
                            IndexedFile(
                                username=canon_user,
                                repo_name=repo_name,
                                file_path=path,
                                file_extension="." + path.split(".")[-1] if "." in path else "",
                                language=f_item.get("language") or main_lang,
                                size=size or len(content),
                                chunk_count=len(file_chunks),
                                sha=f_item.get("sha", ""),
                                source_url=f"{repo_url}/blob/{default_branch}/{path}"
                            )
                        )

                all_chunks.extend(repo_chunks)


                existing_repo = db.query(Repository).filter(
                    Repository.username == canon_user,
                    Repository.name == repo_name
                ).first()

                if not existing_repo:
                    existing_repo = Repository(
                        username=canon_user,
                        name=repo_name,
                        full_name=r.get("full_name"),
                        description=r.get("description"),
                        html_url=repo_url,
                        stars=r.get("stargazers_count", 0),
                        forks=r.get("forks_count", 0),
                        language=main_lang,
                        default_branch=default_branch,
                        file_count=repo_file_count,
                        chunk_count=len(repo_chunks),
                        readme_content=readme_text,
                        last_pushed_at=last_pushed,
                        indexed_at=datetime.now(timezone.utc)
                    )
                    existing_repo.set_topics(r.get("topics", []))
                    db.add(existing_repo)
                else:
                    existing_repo.description = r.get("description")
                    existing_repo.stars = r.get("stargazers_count", 0)
                    existing_repo.forks = r.get("forks_count", 0)
                    existing_repo.file_count = repo_file_count
                    existing_repo.chunk_count = len(repo_chunks)
                    existing_repo.readme_content = readme_text
                    existing_repo.last_pushed_at = last_pushed
                    existing_repo.set_topics(r.get("topics", []))
                    existing_repo.indexed_at = datetime.now(timezone.utc)

                db.flush()
                for chunk in repo_chunks:
                    metadata = chunk["metadata"]
                    metadata["repository_id"] = str(existing_repo.id)
                    metadata["repository_full_name"] = repo_full_name
                    metadata["repository_url"] = repo_url

                processed_repos.append(repo_name)


            self._update_job_status(
                db, canon_user, "processing", 75,
                "Generating embeddings", f"Creating vector embeddings for {len(all_chunks)} chunks..."
            )


            if all_chunks:
                await asyncio.to_thread(vector_store.add_chunks, all_chunks)


            detected_techs = self.github_service.detect_technologies_from_files(
                repo_languages=repo_languages,
                file_paths=all_file_paths_for_tech
            )


            profile = db.query(Profile).filter(Profile.username == canon_user).first()
            if not profile:
                profile = Profile(
                    username=canon_user,
                    name=profile_data["name"],
                    avatar_url=profile_data["avatar_url"],
                    bio=profile_data["bio"],
                    public_repos=profile_data["public_repos"],
                    indexed_repos=len(processed_repos),
                    total_files=len(all_indexed_files),
                    total_chunks=len(all_chunks),
                    status="completed",
                    last_indexed_at=datetime.now(timezone.utc)
                )
                profile.set_languages(detected_techs)
                db.add(profile)
            else:
                profile.name = profile_data["name"]
                profile.avatar_url = profile_data["avatar_url"]
                profile.bio = profile_data["bio"]
                profile.public_repos = profile_data["public_repos"]
                profile.indexed_repos = len(processed_repos)
                profile.total_files = len(all_indexed_files)
                profile.total_chunks = len(all_chunks)
                profile.status = "completed"
                profile.last_indexed_at = datetime.now(timezone.utc)
                profile.set_languages(detected_techs)


            if all_indexed_files:
                db.bulk_save_objects(all_indexed_files)

            db.commit()


            self._update_job_status(
                db, canon_user, "completed", 100,
                "Knowledge base ready",
                f"Successfully indexed {len(processed_repos)} repositories and {len(all_chunks)} code chunks."
            )

        except GitHubAPIError as e:
            logger.error("GitHub API error indexing @%s (status %s)", username, e.status_code)
            profile = db.query(Profile).filter(Profile.username == canon_user).first()
            if profile:
                profile.status = "error"
                db.commit()
            self._update_job_status(
                db, canon_user, "error", 0, "Error",
                "GitHub API request failed. Check the username, network, or GitHub API configuration.",
                error_message="GitHub API request failed. Check the username, network, or GitHub API configuration."
            )
        except Exception as e:
            logger.error(
                "Unexpected indexing error for @%s (%s)",
                username,
                type(e).__name__,
            )
            profile = db.query(Profile).filter(Profile.username == canon_user).first()
            if profile:
                profile.status = "error"
                db.commit()
            self._update_job_status(
                db, canon_user, "error", 0, "Failed",
                "An unexpected error occurred during indexing. Check the server logs.",
                error_message="An unexpected error occurred during indexing. Check the server logs."
            )
        finally:
            db.close()

    def _is_candidate(self, path: str) -> bool:
        from ..utils.file_filters import is_text_file_path
        return is_text_file_path(path)

indexing_service = IndexingService()
