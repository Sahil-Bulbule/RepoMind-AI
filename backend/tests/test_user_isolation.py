import pytest
from backend.app.rag.vector_store import vector_store

def test_user_isolation_guarantee():
    """
    CRITICAL SECURITY & FUNCTIONAL REQUIREMENT:
    Verify that queries for user_alice NEVER retrieve chunks belonging to user_bob,
    even if user_bob has the exact text the user is searching for!
    """

    vector_store.delete_user_knowledge("user_alice")
    vector_store.delete_user_knowledge("user_bob")


def test_repository_identity_filter_excludes_other_repositories_for_same_user():
    username = "repo_boundary_user"
    vector_store.delete_user_knowledge(username)


def test_legacy_repository_chunks_are_backfilled_with_stable_identity():
    username = "legacy_repo_user"
    vector_store.delete_user_knowledge(username)
    vector_store.add_chunks([{
        "chunk_text": "Legacy repository readme describes its purpose.",
        "metadata": {
            "github_username": username,
            "repository_name": "Legacy-Project",
            "repository_url": "https://github.com/legacy_repo_user/Legacy-Project",
            "file_path": "README.md",
            "file_extension": ".md",
            "language": "Markdown",
            "branch": "main",
            "source_url": "https://github.com/legacy_repo_user/Legacy-Project/blob/main/README.md#L1-L1",
            "chunk_index": 0,
            "total_chunks": 1,
            "start_line": 1,
            "end_line": 1,
        },
    }])

    vector_store.ensure_repository_metadata(
        username=username,
        repository_name="Legacy-Project",
        repository_id=77,
        repository_full_name="legacy_repo_user/legacy-project",
        repository_url="https://github.com/legacy_repo_user/Legacy-Project",
    )
    results = vector_store.query(
        username=username,
        query_text="purpose",
        repository_filter="Legacy-Project",
        repository_id=77,
        repository_full_name="legacy_repo_user/legacy-project",
    )

    assert len(results) == 1
    assert results[0]["metadata"]["repository_id"] == "77"
    assert results[0]["metadata"]["repository_full_name"] == "legacy_repo_user/legacy-project"
    vector_store.delete_user_knowledge(username)
    chunks = []
    for repo_name, repository_id, full_name, content in [
        (
            "Folder-Size-Analyzer",
            "101",
            "repo_boundary_user/folder-size-analyzer",
            "FolderSizeAnalyzer recursively measures directory sizes with os.walk.",
        ),
        (
            "LEETCODE",
            "202",
            "repo_boundary_user/leetcode",
            "This implementation uses TensorFlow CNN Conv2D model training in model.py.",
        ),
    ]:
        chunks.append({
            "chunk_text": content,
            "metadata": {
                "github_username": username,
                "repository_name": repo_name,
                "repository_full_name": full_name,
                "repository_id": repository_id,
                "repository_url": f"https://github.com/{full_name}",
                "file_path": "model.py" if repo_name == "LEETCODE" else "main.py",
                "file_extension": ".py",
                "language": "Python",
                "branch": "main",
                "source_url": f"https://github.com/{full_name}/blob/main/main.py#L1-L2",
                "chunk_index": 0,
                "total_chunks": 1,
                "start_line": 1,
                "end_line": 2,
            },
        })

    vector_store.add_chunks(chunks)
    results = vector_store.query(
        username=username,
        query_text="TensorFlow CNN Conv2D model",
        repository_filter="Folder-Size-Analyzer",
        repository_id=101,
        repository_full_name="repo_boundary_user/folder-size-analyzer",
        top_k=8,
    )
    keyword_results = vector_store.keyword_query(
        username=username,
        query_text="TensorFlow CNN model",
        repository_filter="Folder-Size-Analyzer",
        repository_id=101,
        repository_full_name="repo_boundary_user/folder-size-analyzer",
    )

    assert results
    assert all(item["metadata"]["repository_name"] == "Folder-Size-Analyzer" for item in results)
    assert all(item["metadata"]["repository_id"] == "101" for item in results)
    assert keyword_results == []

    vector_store.delete_user_knowledge(username)


    alice_chunks = [
        {
            "chunk_text": "Alice's web server uses FastAPI and PostgreSQL database.",
            "metadata": {
                "github_username": "user_alice",
                "repository_name": "alice-api",
                "repository_url": "https://github.com/user_alice/alice-api",
                "file_path": "main.py",
                "file_extension": ".py",
                "language": "Python",
                "branch": "main",
                "source_url": "https://github.com/user_alice/alice-api/blob/main/main.py#L1-L10",
                "chunk_index": 0,
                "total_chunks": 1,
                "start_line": 1,
                "end_line": 10
            }
        }
    ]


    bob_chunks = [
        {
            "chunk_text": "Bob's project NEO-Inspect implements a Convolutional Neural Network with TensorFlow.",
            "metadata": {
                "github_username": "user_bob",
                "repository_name": "neo-inspect",
                "repository_url": "https://github.com/user_bob/neo-inspect",
                "file_path": "model.py",
                "file_extension": ".py",
                "language": "Python",
                "branch": "main",
                "source_url": "https://github.com/user_bob/neo-inspect/blob/main/model.py#L1-L10",
                "chunk_index": 0,
                "total_chunks": 1,
                "start_line": 1,
                "end_line": 10
            }
        }
    ]

    vector_store.add_chunks(alice_chunks)
    vector_store.add_chunks(bob_chunks)



    alice_results = vector_store.query(
        username="user_alice",
        query_text="Convolutional Neural Network and TensorFlow",
        top_k=5
    )

    for r in alice_results:
        assert r["metadata"]["github_username"] == "user_alice"
        assert r["metadata"]["repository_name"] != "neo-inspect"


    bob_results = vector_store.query(
        username="user_bob",
        query_text="Convolutional Neural Network and TensorFlow",
        top_k=5
    )

    assert len(bob_results) > 0
    assert bob_results[0]["metadata"]["github_username"] == "user_bob"
    assert bob_results[0]["metadata"]["repository_name"] == "neo-inspect"


    bob_filtered_results = vector_store.query(
        username="user_bob",
        query_text="Convolutional Neural Network",
        repository_filter="other-repo",
        top_k=5
    )

    assert len(bob_filtered_results) == 0


    vector_store.delete_user_knowledge("user_alice")
    vector_store.delete_user_knowledge("user_bob")
