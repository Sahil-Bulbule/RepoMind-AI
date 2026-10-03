from backend.app.rag.chunker import CodeTextChunker

def test_chunker_basic():
    chunker = CodeTextChunker(chunk_size=100, chunk_overlap=20)
    sample_code = """import os

class ModelTrainer:
    def __init__(self, lr=0.01):
        self.lr = lr

    def train(self, data):
        print("Training model...")
        return True
"""
    chunks = chunker.chunk_file(
        username="TestUser",
        repo_name="my-project",
        repo_url="https://github.com/TestUser/my-project",
        file_path="src/trainer.py",
        branch="main",
        content=sample_code
    )

    assert len(chunks) > 0
    first = chunks[0]
    assert "chunk_text" in first
    assert "metadata" in first
    meta = first["metadata"]

    assert meta["github_username"] == "testuser"
    assert meta["repository_name"] == "my-project"
    assert meta["file_path"] == "src/trainer.py"
    assert meta["language"] == "Python"
    assert meta["branch"] == "main"
    assert "https://github.com/TestUser/my-project/blob/main/src/trainer.py#L" in meta["source_url"]
    assert meta["start_line"] >= 1
    assert meta["end_line"] >= meta["start_line"]

def test_chunker_empty_content():
    chunker = CodeTextChunker()
    chunks = chunker.chunk_file(
        username="TestUser",
        repo_name="my-project",
        repo_url="https://github.com/TestUser/my-project",
        file_path="empty.py",
        branch="main",
        content=""
    )
    assert chunks == []
