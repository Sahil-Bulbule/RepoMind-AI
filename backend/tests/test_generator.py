import asyncio

from backend.app.rag.generator import AnswerGenerator
from backend.app.rag.generator import SYSTEM_INSTRUCTIONS
from backend.app.schemas.schemas import ChatMessage


def test_generator_uses_groq_chat_completions(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "Grounded answer"}}]}

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, headers, json):
            captured.update(url=url, headers=headers, payload=json)
            return FakeResponse()

    answer_generator = AnswerGenerator()
    monkeypatch.setattr("backend.app.rag.generator.settings.GROQ_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.rag.generator.httpx.AsyncClient", FakeClient)

    answer = asyncio.run(
        answer_generator.generate_answer(
            username="example",
            question="What file is present?",
            context_text="Repository demo contains app.py.",
                conversation_history=[
                    ChatMessage(role="user", content="What project is this?"),
                    ChatMessage(role="assistant", content="RETAIN---IQ uses an ANN."),
                    ChatMessage(role="user", content="What file is present?"),
                ],
                repository_filter="NEO-Inspect",
                repository_full_name="repo-owner/neo-inspect",
        )
    )

    assert answer == "Grounded answer"
    assert captured["url"].endswith("/chat/completions")
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == answer_generator.model_name
    system_message = captured["payload"]["messages"][0]
    assert system_message["role"] == "system"
    assert "NEO-Inspect" in system_message["content"]
    assert "repo-owner/neo-inspect" in system_message["content"]
    assert "ONLY the selected GitHub repository" in system_message["content"]
    assert all(message["role"] == "user" for message in captured["payload"]["messages"][1:])
    assert "RETAIN---IQ" not in str(captured["payload"]["messages"])


def test_generator_reports_missing_groq_api_key(monkeypatch):
    answer_generator = AnswerGenerator()
    monkeypatch.setattr("backend.app.rag.generator.settings.GROQ_API_KEY", "")

    answer = asyncio.run(
        answer_generator.generate_answer(
            username="example",
            question="What file is present?",
            context_text="Repository demo contains app.py.",
            conversation_history=[],
        )
    )

    assert "GROQ_API_KEY" in answer
