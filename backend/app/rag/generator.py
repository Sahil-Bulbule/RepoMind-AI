import logging
from typing import List, Optional
import httpx
from ..config import settings
from ..schemas.schemas import ChatMessage

logger = logging.getLogger("ask_my_github")

SYSTEM_INSTRUCTIONS = """You are "Ask My GitHub", a premier AI assistant analyzing a developer's public GitHub portfolio.
Your mission is to provide accurate, deeply grounded, and professional explanations of repositories, codebases, architectures, and technologies.

GROUNDING AND ANSWER RULES:
1. Use supplied repository code, README, repository metadata, and relevant conversation history as evidence for repository-specific claims.
2. Never invent repository names, file paths, functions, dependencies, or project features. Say when a repository-specific detail is absent from the supplied context.
3. Answer general programming questions from general knowledge when useful, and label that explanation as general guidance rather than claiming it describes the indexed repository.
4. For explanations, summaries, comparisons, and recommendations, give the best supported answer from the available context instead of refusing just because an exact phrase was not found.
5. Identify repositories and file paths supporting code-specific claims. Distinguish direct evidence from reasonable inference.
6. For follow-ups, resolve pronouns using previous turns and the active repository scope.
7. Use fenced code blocks for code and concise headings or bullets when useful.
8. Be concise, developer-focused, and direct.
"""

REPOSITORY_SYSTEM_INSTRUCTIONS = """You are answering questions about ONLY the selected GitHub repository.
You must answer ONLY from retrieved evidence belonging to this repository. Never use information from another repository.
Never assume a technology, file, function, model, database, or feature exists unless the retrieved evidence proves it.
Use the selected repository's supplied code, README, and metadata as evidence. Never invent files or features. Answer general programming questions with clearly labeled general guidance, and state when repository-specific details are absent from the supplied context. Prefer a useful, qualified answer over a generic refusal.
"""

class AnswerGenerator:
    def __init__(self):
        self.model_name = settings.GROQ_MODEL

    async def generate_answer(
        self,
        username: str,
        question: str,
        context_text: str,
        conversation_history: List[ChatMessage],
        repository_filter: Optional[str] = None,
        repository_full_name: Optional[str] = None,
    ) -> str:
        """
        Generate a grounded answer using the configured chat completion service.
        """
        if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
            return (
                "**AI API key missing**\n\n"
                "Set `GROQ_API_KEY` in `backend/.env` to enable AI responses. "
                "Create or rotate your key at [Groq Console](https://console.groq.com/keys)."
            )


        repo_scope = f"Scope: Repository '{repository_filter}'" if repository_filter else "Scope: All Indexed Repositories"
        

        history_formatted = ""
        if conversation_history:
            recent_turns = conversation_history[-6:]
            if repository_filter:
                recent_turns = [message for message in recent_turns if message.role == "user"]
            formatted_turns = []
            for m in recent_turns:
                prefix = "User" if m.role == "user" else "Assistant"
                formatted_turns.append(f"{prefix}: {m.content}")
            history_formatted = "Recent Conversation History:\n" + "\n".join(formatted_turns) + "\n\n"

        prompt = f"""Target GitHub Profile: @{username}
{repo_scope}

{history_formatted}=== RETRIEVED REPOSITORY CONTEXT ===
{context_text}
=== END CONTEXT ===

User Question: {question}

Please answer the user's question accurately using only the repository evidence above:"""

        system_instructions = SYSTEM_INSTRUCTIONS
        if repository_filter:
            system_instructions = (
                f"{SYSTEM_INSTRUCTIONS}\n\n{REPOSITORY_SYSTEM_INSTRUCTIONS}\n\n"
                f"Selected repository: {repository_filter}\n"
                f"Canonical repository: {repository_full_name or repository_filter}\n"
                f"GitHub owner: {username}"
            )
        messages = [{"role": "system", "content": system_instructions}]
        recent_turns = conversation_history[-6:]
        if recent_turns and recent_turns[-1].role == "user" and recent_turns[-1].content == question:
            recent_turns = recent_turns[:-1]
        messages.extend(
            {"role": message.role, "content": message.content}
            for message in recent_turns
            if not repository_filter or message.role == "user"
        )
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY.strip()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 1500,
                    },
                )
            if response.status_code == 429:
                return "The AI service rate limit has been reached. Please try again shortly."
            if response.status_code in (401, 403):
                return "The AI service rejected its API key. Check the backend configuration."
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if isinstance(content, str) and content.strip():
                return content.strip()
            if repository_filter:
                return "I couldn't find enough evidence in this repository to answer that confidently."
            return "I couldn't find enough evidence in the indexed repositories to answer that confidently."
        except httpx.HTTPStatusError as e:
            logger.error("AI service request failed with HTTP %s", e.response.status_code)
            return f"The AI service returned HTTP {e.response.status_code}. Check the model and API settings."
        except httpx.HTTPError as e:
            logger.error("AI service connection failed: %s", type(e).__name__)
            return "Could not connect to the AI service. Check your network connection and try again."
        except Exception as e:
            logger.error("AI service response parsing failed (%s)", type(e).__name__)
            return "An error occurred while contacting the AI model. Check the server configuration."

generator = AnswerGenerator()
