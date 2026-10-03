from backend.app.api import routes_chat, routes_search
from backend.app.models.database import IndexedFile, Profile, Repository

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "chroma_status" in data

def test_analyze_invalid_username(client):
    response = client.post("/api/github/analyze", json={"username": "invalid--user"})
    assert response.status_code == 400
    assert "Invalid GitHub username" in response.json()["detail"]

def test_analyze_empty_username(client):
    response = client.post("/api/github/analyze", json={"username": ""})
    assert response.status_code == 422

def test_chat_non_indexed_user(client):
    response = client.post("/api/chat", json={
        "github_username": "non-indexed-user",
        "message": "What projects do you have?"
    })
    assert response.status_code == 404
    assert "has not been indexed yet" in response.json()["detail"]

def test_chat_empty_message(client, db_session):

    p = Profile(username="mockuser", status="completed", public_repos=1)
    db_session.add(p)
    db_session.commit()

    response = client.post("/api/chat", json={
        "github_username": "mockuser",
        "message": "   "
    })
    assert response.status_code == 400
    assert "Message cannot be empty" in response.json()["detail"]

def test_profile_summary_uses_indexed_repository_metadata(client, db_session, monkeypatch):
    profile = Profile(
        username="summary-user",
        name="Summary User",
        bio="Builds developer tools",
        public_repos=1,
        indexed_repos=1,
        total_files=12,
        status="completed",
    )
    profile.set_languages(["Python"])
    repository = Repository(
        username="summary-user",
        name="portfolio-tool",
        description="A tool for exploring developer portfolios",
        html_url="https://github.com/summary-user/portfolio-tool",
        stars=7,
        language="Python",
        file_count=12,
        chunk_count=8,
    )
    db_session.add_all([profile, repository])
    db_session.commit()

    captured = {}

    def empty_retrieval(**kwargs):
        return [], []

    async def capture_generation(**kwargs):
        captured.update(kwargs)
        return "Portfolio summary"

    monkeypatch.setattr(routes_chat.retriever, "retrieve", empty_retrieval)
    monkeypatch.setattr(routes_chat.generator, "generate_answer", capture_generation)

    response = client.post("/api/chat", json={
        "github_username": "summary-user",
        "message": "Summarize this GitHub profile",
    })

    assert response.status_code == 200
    assert response.json()["answer"] == "Portfolio summary"
    assert "portfolio-tool" in captured["context_text"]
    assert "developer portfolios" in captured["context_text"]
    assert "Python" in captured["context_text"]


def test_chat_is_available_while_repository_indexing_continues(client, db_session, monkeypatch):
    profile = Profile(
        username="early-chat-user",
        public_repos=1,
        indexed_repos=0,
        status="indexing",
    )
    repository = Repository(
        username="early-chat-user",
        name="in-progress-project",
        full_name="early-chat-user/in-progress-project",
        description="A project whose source indexing is still running",
        html_url="https://github.com/early-chat-user/in-progress-project",
        language="Python",
    )
    db_session.add_all([profile, repository])
    db_session.commit()

    captured = {}

    def empty_retrieval(**kwargs):
        return [], []

    async def capture_generation(**kwargs):
        captured.update(kwargs)
        return "An early answer from available repository metadata."

    monkeypatch.setattr(routes_chat.retriever, "retrieve", empty_retrieval)
    monkeypatch.setattr(routes_chat.generator, "generate_answer", capture_generation)

    response = client.post("/api/chat", json={
        "github_username": "early-chat-user",
        "message": "What is this project about?",
    })

    assert response.status_code == 200
    assert response.json()["answer"] == "An early answer from available repository metadata."
    assert "in-progress-project" in captured["context_text"]
    assert "A project whose source indexing is still running" in captured["context_text"]


def test_portfolio_technology_question_uses_repository_metadata(client, db_session, monkeypatch):
    profile = Profile(
        username="stack-user",
        public_repos=2,
        indexed_repos=2,
        status="completed",
    )
    profile.set_languages(["Python", "JavaScript"])
    python_repository = Repository(
        username="stack-user",
        name="api-service",
        description="Backend API",
        html_url="https://github.com/stack-user/api-service",
        language="Python",
        file_count=8,
    )
    javascript_repository = Repository(
        username="stack-user",
        name="web-client",
        description="Frontend application",
        html_url="https://github.com/stack-user/web-client",
        language="JavaScript",
        file_count=5,
    )
    db_session.add_all([profile, python_repository, javascript_repository])
    db_session.commit()

    captured = {}

    def empty_retrieval(**kwargs):
        return [], []

    async def capture_generation(**kwargs):
        captured.update(kwargs)
        return "Repository technology summary"

    monkeypatch.setattr(routes_chat.retriever, "retrieve", empty_retrieval)
    monkeypatch.setattr(routes_chat.generator, "generate_answer", capture_generation)

    response = client.post("/api/chat", json={
        "github_username": "stack-user",
        "message": "Show the technology stack breakdown across all projects",
    })

    assert response.status_code == 200
    assert response.json()["answer"] == "Repository technology summary"
    assert "api-service" in captured["context_text"]
    assert "Language: Python" in captured["context_text"]
    assert "web-client" in captured["context_text"]
    assert "Language: JavaScript" in captured["context_text"]


def test_chat_rejects_repository_identity_mismatch(client, db_session):
    profile = Profile(username="repo-owner", status="completed")
    repository = Repository(
        id=42,
        username="repo-owner",
        name="NEO-Inspect",
        full_name="repo-owner/NEO-Inspect",
        html_url="https://github.com/repo-owner/NEO-Inspect",
    )
    db_session.add_all([profile, repository])
    db_session.commit()

    response = client.post("/api/chat", json={
        "github_username": "repo-owner",
        "repository_id": 99,
        "repository_name": "NEO-Inspect",
        "repository_full_name": "repo-owner/NEO-Inspect",
        "repository_url": "https://github.com/repo-owner/NEO-Inspect",
        "question": "How does it work?",
    })

    assert response.status_code == 404
    assert "selected repository" in response.json()["detail"]


def test_repository_chat_passes_resolved_identity_to_retrieval(client, db_session, monkeypatch):
    profile = Profile(username="repo-owner", status="completed")
    repository = Repository(
        id=42,
        username="repo-owner",
        name="NEO-Inspect",
        full_name="repo-owner/NEO-Inspect",
        html_url="https://github.com/repo-owner/NEO-Inspect",
    )
    db_session.add_all([profile, repository])
    db_session.commit()

    captured = {}

    def capture_retrieval(**kwargs):
        captured.update(kwargs)
        return ([{
            "content": "model.py defines the repository model.",
            "metadata": {
                "github_username": "repo-owner",
                "repository_name": "NEO-Inspect",
                "repository_full_name": "repo-owner/neo-inspect",
                "repository_id": "42",
                "file_path": "model.py",
                "language": "Python",
                "start_line": 1,
                "end_line": 1,
                "source_url": "https://github.com/repo-owner/NEO-Inspect/blob/main/model.py#L1-L1",
            },
        }], [])

    async def capture_generation(**kwargs):
        captured.update(generation=kwargs)
        return "Scoped answer"

    monkeypatch.setattr(routes_chat.vector_store, "ensure_repository_metadata", lambda **kwargs: None)
    monkeypatch.setattr(routes_chat.retriever, "retrieve", capture_retrieval)
    monkeypatch.setattr(routes_chat.generator, "generate_answer", capture_generation)

    response = client.post("/api/chat", json={
        "github_username": "repo-owner",
        "repository_id": 42,
        "repository_name": "NEO-Inspect",
        "repository_full_name": "repo-owner/NEO-Inspect",
        "repository_url": "https://github.com/repo-owner/NEO-Inspect",
        "question": "Where is the model defined?",
    })

    assert response.status_code == 200
    assert captured["username"] == "repo-owner"
    assert captured["repository_filter"] == "NEO-Inspect"
    assert captured["repository_id"] == 42
    assert captured["repository_full_name"] == "repo-owner/neo-inspect"
    assert captured["repository_url"] == "https://github.com/repo-owner/NEO-Inspect"
    assert captured["generation"]["repository_full_name"] == "repo-owner/neo-inspect"


def test_repository_suggestions_use_each_repositories_indexed_files(client, db_session):
    profile = Profile(username="suggest-user", status="completed")
    folder_repo = Repository(
        username="suggest-user",
        name="Folder-Size-Analyzer",
        full_name="suggest-user/Folder-Size-Analyzer",
        html_url="https://github.com/suggest-user/Folder-Size-Analyzer",
        language="Python",
        readme_content="# Directory Analysis\nMeasures nested folders.",
    )
    portfolio_repo = Repository(
        username="suggest-user",
        name="Portfolio-",
        full_name="suggest-user/Portfolio-",
        html_url="https://github.com/suggest-user/Portfolio-",
        language="JavaScript",
        readme_content="# Portfolio UI\nReact-based portfolio site.",
    )
    db_session.add_all([profile, folder_repo, portfolio_repo])
    db_session.flush()
    db_session.add_all([
        IndexedFile(
            username="suggest-user",
            repo_name="Folder-Size-Analyzer",
            file_path="folder_analyzer/main.py",
            file_extension=".py",
            language="Python",
            source_url="https://github.com/suggest-user/Folder-Size-Analyzer/blob/main/folder_analyzer/main.py",
        ),
        IndexedFile(
            username="suggest-user",
            repo_name="Portfolio-",
            file_path="src/components/Hero.jsx",
            file_extension=".jsx",
            language="JavaScript",
            source_url="https://github.com/suggest-user/Portfolio-/blob/main/src/components/Hero.jsx",
        ),
    ])
    db_session.commit()

    folder_questions = client.get(
        f"/api/github/repository/suggest-user/id/{folder_repo.id}/suggestions"
    ).json()["questions"]
    portfolio_questions = client.get(
        f"/api/github/repository/suggest-user/id/{portfolio_repo.id}/suggestions"
    ).json()["questions"]

    assert 4 <= len(folder_questions) <= 6
    assert 4 <= len(portfolio_questions) <= 6
    assert folder_questions != portfolio_questions
    assert any("main.py" in question or "Directory Analysis" in question for question in folder_questions)
    assert any("Hero.jsx" in question or "Portfolio UI" in question for question in portfolio_questions)


def test_code_search_returns_repository_matches_with_file_evidence(client, db_session, monkeypatch):
    profile = Profile(username="search-user", status="completed")
    matching_repo = Repository(
        username="search-user",
        name="ml-toolkit",
        full_name="search-user/ml-toolkit",
        description="Machine learning utilities",
        html_url="https://github.com/search-user/ml-toolkit",
        language="Python",
    )
    other_repo = Repository(
        username="search-user",
        name="web-dashboard",
        full_name="search-user/web-dashboard",
        html_url="https://github.com/search-user/web-dashboard",
        language="JavaScript",
    )
    db_session.add_all([profile, matching_repo, other_repo])
    db_session.commit()

    captured = {}

    def fake_search(**kwargs):
        captured.update(kwargs)
        return [
            {
                "content": "raw machine learning source must not be returned",
                "metadata": {
                    "repository_name": "ml-toolkit",
                    "file_path": "src/model.py",
                    "source_url": "https://github.com/search-user/ml-toolkit/blob/main/src/model.py",
                    "language": "Python",
                },
                "score": 0.82,
            },
            {
                "content": "another raw chunk",
                "metadata": {
                    "repository_name": "ml-toolkit",
                    "file_path": "README.md",
                    "source_url": "https://github.com/search-user/ml-toolkit/blob/main/README.md",
                    "language": "Markdown",
                },
                "score": 0.74,
            },
            {
                "content": "separate repo evidence",
                "metadata": {
                    "repository_name": "web-dashboard",
                    "file_path": "src/App.jsx",
                    "source_url": "https://github.com/search-user/web-dashboard/blob/main/src/App.jsx",
                    "language": "JavaScript",
                },
                "score": 0.51,
            },
        ]

    monkeypatch.setattr(routes_search.vector_store, "lexical_search", fake_search)
    response = client.post("/api/search", json={
        "github_username": "search-user",
        "query": "machine learning",
        "limit": 10,
    })

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 2
    assert data["results"][0]["repository_full_name"] == "search-user/ml-toolkit"
    assert data["results"][0]["matching_files"] == 2
    assert [item["file_path"] for item in data["results"][0]["evidence_files"]] == [
        "src/model.py",
        "README.md",
    ]
    assert "snippet" not in data["results"][0]
    assert all("content" not in item for item in data["results"])
    assert captured["top_k"] == 5000


def test_code_search_limits_results_to_three_repositories(client, db_session, monkeypatch):
    db_session.add(Profile(username="three-repos", status="completed"))
    repositories = [
        Repository(
            username="three-repos",
            name=f"keyword-repo-{index}",
            full_name=f"three-repos/keyword-repo-{index}",
            html_url=f"https://github.com/three-repos/keyword-repo-{index}",
        )
        for index in range(4)
    ]
    db_session.add_all(repositories)
    db_session.commit()

    def fake_search(**kwargs):
        return [
            {
                "metadata": {
                    "repository_name": repository.name,
                    "file_path": "src/match.py",
                    "source_url": repository.html_url,
                    "language": "Python",
                },
                "score": 0.9,
            }
            for repository in repositories
        ]

    monkeypatch.setattr(routes_search.vector_store, "lexical_search", fake_search)
    response = client.post("/api/search", json={
        "github_username": "three-repos",
        "query": "keyword",
        "limit": 50,
    })

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 3
    assert len(data["results"]) == 3


def test_lexical_search_requires_all_terms_and_filters_by_profile_and_repository():
    from backend.app.rag.vector_store import VectorStore

    records = [
        {
            "ids": ["relevant", "missing-auth", "missing-jwt", "substring-only", "metadata-only"],
            "documents": [
                "JWT authentication middleware validates each request.",
                "Authentication middleware validates user sessions.",
                "JWT decoder reads signed tokens.",
                "preJWTpost authentication middleware",
                "A plain utility function with no matching keywords.",
            ],
            "metadatas": [
                {"repository_name": "auth-api", "file_path": "auth.py", "language": "Python"},
                {"repository_name": "auth-api", "file_path": "sessions.py", "language": "Python"},
                {"repository_name": "auth-api", "file_path": "tokens.py", "language": "Python"},
                {"repository_name": "auth-api", "file_path": "legacy.py", "language": "Python"},
                {"repository_name": "jwt-authentication", "file_path": "plain.py", "language": "JWT authentication"},
            ],
        }
    ]

    class FakeCollection:
        def get(self, **kwargs):
            assert kwargs["where"]["$and"][0]["github_username"]["$eq"] == "search-user"
            assert kwargs["where"]["$and"][1]["repository_name"]["$eq"] == "auth-api"
            return records[0]

    store = VectorStore.__new__(VectorStore)
    store.collection = FakeCollection()

    assert store._search_terms("Where is the implementation?") == []
    results = store.lexical_search(
        username="search-user",
        query_text="JWT authentication",
        repository_filter="auth-api",
    )

    assert [result["id"] for result in results] == ["relevant"]
    assert results[0]["score"] > 0

def test_status_endpoint(client):
    response = client.get("/api/github/status/anyuser")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "anyuser"
    assert data["status"] in ["idle", "processing", "completed"]
