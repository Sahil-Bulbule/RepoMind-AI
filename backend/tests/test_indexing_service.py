import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.database import Base, Profile, Repository
from backend.app.services import indexing_service as indexing_module


@pytest.mark.asyncio
async def test_repository_tree_and_readme_fetches_run_concurrently(monkeypatch):
    active_requests = 0
    max_active_requests = 0

    class FakeGitHubService:
        async def _request(self):
            nonlocal active_requests, max_active_requests
            active_requests += 1
            max_active_requests = max(max_active_requests, active_requests)
            await asyncio.sleep(0.01)
            active_requests -= 1

        async def get_repository_tree(self, owner, repo, branch):
            await self._request()
            return [{"path": "main.py"}]

        async def get_readme(self, owner, repo):
            await self._request()
            return f"# {repo}"

    service = FakeGitHubService()
    monkeypatch.setattr(indexing_module.indexing_service, "github_service", service)
    semaphore = asyncio.Semaphore(4)
    results = await asyncio.gather(*(
        indexing_module.indexing_service._fetch_repository_sources(
            "owner",
            {"name": f"repo-{index}", "default_branch": "main"},
            semaphore,
        )
        for index in range(3)
    ))

    assert max_active_requests == 4
    assert all(tree and readme for tree, readme in results)


@pytest.mark.asyncio
async def test_repository_metadata_is_available_before_code_scanning(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session_factory = sessionmaker(bind=engine)
    discovered_repository_count = []

    repositories = [
        {
            "id": index,
            "name": f"repo-{index}",
            "full_name": f"fast-user/repo-{index}",
            "html_url": f"https://github.com/fast-user/repo-{index}",
            "language": "Python",
            "default_branch": "main",
            "fork": index == 0,
        }
        for index in range(1, 4)
    ]

    class FakeGitHubService:
        async def get_user_profile(self, username):
            return {
                "username": username,
                "name": username,
                "avatar_url": "",
                "bio": "",
                "public_repos": len(repositories),
            }

        async def get_user_repositories(self, username):
            return repositories

        async def get_repository_tree(self, owner, repo, branch):
            with test_session_factory() as db:
                discovered_repository_count.append(
                    db.query(Repository).filter(
                        Repository.username == owner.lower()
                    ).count()
                )
            return []

        async def get_readme(self, owner, repo):
            return None

        def detect_technologies_from_files(self, repo_languages, file_paths):
            return list(dict.fromkeys(repo_languages))

    monkeypatch.setattr(indexing_module, "SessionLocal", test_session_factory)
    monkeypatch.setattr(
        indexing_module.indexing_service,
        "github_service",
        FakeGitHubService(),
    )
    monkeypatch.setattr(
        indexing_module.vector_store,
        "delete_user_knowledge",
        lambda username: None,
    )

    try:
        await indexing_module.indexing_service.run_indexing_pipeline("fast-user")

        assert discovered_repository_count == [3, 3, 3]
        with test_session_factory() as db:
            profile = db.query(Profile).filter(Profile.username == "fast-user").one()
            assert profile.status == "completed"
            assert profile.public_repos == 3
            assert db.query(Repository).filter(
                Repository.username == "fast-user"
            ).count() == 3
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
