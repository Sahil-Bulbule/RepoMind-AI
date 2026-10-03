from backend.app.rag import retriever as retriever_module
from backend.app.rag.retriever import GitHubRetriever


def test_exact_keyword_evidence_is_prioritized_over_full_semantic_results(monkeypatch):
    irrelevant_results = [
        {
            "content": f"Unrelated source code chunk {index}.",
            "metadata": {
                "github_username": "query-user",
                "repository_name": f"unrelated-{index}",
                "repository_full_name": f"query-user/unrelated-{index}",
                "repository_id": str(index),
                "file_path": f"src/file_{index}.py",
                "source_url": f"https://github.com/query-user/unrelated-{index}/blob/main/src/file_{index}.py",
                "language": "Python",
                "start_line": 1,
                "end_line": 2,
            },
            "score": 0.8,
        }
        for index in range(2)
    ]
    exact_result = {
        "content": "This project uses Python for its API.",
        "metadata": {
            "github_username": "query-user",
            "repository_name": "python-api",
            "repository_full_name": "query-user/python-api",
            "repository_id": "3",
            "file_path": "app/main.py",
            "source_url": "https://github.com/query-user/python-api/blob/main/app/main.py",
            "language": "Python",
            "start_line": 1,
            "end_line": 2,
        },
        "score": 0.65,
        "matched_term_count": 1,
    }
    keyword_query_calls = []

    monkeypatch.setattr(
        retriever_module.vector_store,
        "query",
        lambda **kwargs: irrelevant_results,
    )

    def keyword_query(**kwargs):
        keyword_query_calls.append(kwargs)
        return [exact_result]

    monkeypatch.setattr(retriever_module.vector_store, "keyword_query", keyword_query)

    chunks, citations = GitHubRetriever().retrieve(
        username="query-user",
        query="Which indexed repositories use Python?",
        top_k=2,
    )

    assert keyword_query_calls
    assert chunks[0]["metadata"]["repository_name"] == "python-api"
    assert citations[0].repository_name == "python-api"


def test_profile_metadata_question_detects_repository_language_queries():
    from backend.app.api.routes_chat import _is_profile_overview_request

    assert _is_profile_overview_request("Which indexed repositories use Python?")
    assert _is_profile_overview_request("What languages do my projects use?")
