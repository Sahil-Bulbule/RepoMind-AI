import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.github_service import GitHubService, GitHubAPIError

def test_detect_technologies_heuristics():
    service = GitHubService()
    detected = service.detect_technologies_from_files(
        repo_languages=["Python", "TypeScript"],
        file_paths=[
            "frontend/src/App.tsx",
            "frontend/package.json",
            "backend/app/main.py",
            "Dockerfile"
        ],
        readme_text="A fullstack app with FastAPI, React, and MongoDB."
    )

    assert "Python" in detected
    assert "TypeScript" in detected
    assert "React" in detected
    assert "FastAPI" in detected
    assert "MongoDB" in detected
    assert "Docker" in detected

@pytest.mark.asyncio
async def test_get_user_profile_invalid_user():
    service = GitHubService()
    with pytest.raises(GitHubAPIError) as exc_info:
        await service.get_user_profile("-invalid-username")
    assert "Invalid GitHub username format" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_get_user_repositories_fetches_all_pages_including_forks(monkeypatch):
    from backend.app.services import github_service

    requested_pages = []

    class FakeResponse:
        status_code = 200
        headers = {}
        text = ""

        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, headers, params):
            requested_pages.append(params["page"])
            if params["page"] == 1:
                return FakeResponse([
                    {
                        "name": f"repo-{index}",
                        "fork": index == 0,
                        "private": index == 1,
                    }
                    for index in range(100)
                ])
            return FakeResponse([{"name": "repo-100"}, {"name": "repo-101"}])

    monkeypatch.setattr(github_service.httpx, "AsyncClient", FakeClient)
    repositories = await GitHubService().get_user_repositories("repo-owner")

    assert len(repositories) == 101
    assert repositories[0]["fork"] is True
    assert all(not repository.get("private", False) for repository in repositories)
    assert "repo-1" not in {repository["name"] for repository in repositories}
    assert requested_pages == [1, 2]
