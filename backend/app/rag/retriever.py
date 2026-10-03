from typing import List, Dict, Any, Optional, Tuple
import re
from .vector_store import vector_store
from ..schemas.schemas import SourceCitation

class GitHubRetriever:
    def __init__(self, min_score_threshold: float = 0.30):
        self.min_score_threshold = min_score_threshold

    @staticmethod
    def _expand_query(query: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_./ -]", " ", query).casefold()
        expansions = {
            "cnn": "convolution conv2d keras tensorflow pytorch model",
            "model": "cnn conv2d keras tensorflow pytorch architecture",
            "defect": "inspection classification inference detection",
            "language": "python javascript typescript java",
        }
        terms = normalized.split()
        expanded = list(terms)
        for term in terms:
            expanded.extend(expansions.get(term, "").split())
        return " ".join(dict.fromkeys(expanded))

    def retrieve(
        self,
        username: str,
        query: str,
        repository_filter: Optional[str] = None,
        repository_id: Optional[int] = None,
        repository_full_name: Optional[str] = None,
        repository_url: Optional[str] = None,
        conversation_history: Optional[List[Any]] = None,
        top_k: int = 8
    ) -> Tuple[List[Dict[str, Any]], List[SourceCitation]]:
        """
        Retrieves relevant repository chunks, deduplicates, and formats citations.
        """
        normalized_query = " ".join(query.split())
        if repository_filter and len(normalized_query.split()) < 8 and conversation_history:
            previous_questions = [
                message.content
                for message in conversation_history
                if message.role == "user" and message.content.strip() != query.strip()
            ]
            if previous_questions:
                normalized_query = f"{previous_questions[-1]} Follow-up: {normalized_query}"

        raw_results = vector_store.query(
            username=username,
            query_text=self._expand_query(normalized_query),
            repository_filter=repository_filter,
            repository_id=repository_id,
            repository_full_name=repository_full_name,
            top_k=top_k * 2
        )

        is_repository_scoped = bool(repository_filter and repository_full_name and repository_id is not None)
        if is_repository_scoped:
            raw_results = [
                item for item in raw_results
                if item["metadata"].get("github_username", "").casefold() == username.casefold()
                and item["metadata"].get("repository_name", "").casefold() == repository_filter.casefold()
                and str(item["metadata"].get("repository_id", "")) == str(repository_id)
                and item["metadata"].get("repository_full_name", "").casefold() == repository_full_name.casefold()
                and (
                    not repository_url
                    or item["metadata"].get("source_url", "").casefold().startswith(repository_url.rstrip("/").casefold() + "/")
                )
            ]

        filtered_results = []
        seen_keys = set()

        for item in raw_results:
            meta = item["metadata"]
            score = item.get("score", 0.0)

            if score < self.min_score_threshold:
                continue


            dedup_key = f"{meta.get('repository_name')}:{meta.get('file_path')}:{meta.get('start_line')}"
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            filtered_results.append(item)

        if top_k > 0:
            keyword_results = vector_store.keyword_query(
                username=username,
                query_text=normalized_query,
                repository_filter=repository_filter,
                repository_id=repository_id,
                repository_full_name=repository_full_name,
                top_k=top_k * 3,
            )
            known_keys = {
                f"{item['metadata'].get('repository_name')}:{item['metadata'].get('file_path')}:{item['metadata'].get('start_line')}"
                for item in filtered_results
            }
            for item in keyword_results:
                meta = item["metadata"]
                if (
                    meta.get("github_username", "").casefold() != username.casefold()
                    or (
                        is_repository_scoped
                        and (
                            meta.get("repository_name", "").casefold() != repository_filter.casefold()
                            or str(meta.get("repository_id", "")) != str(repository_id)
                            or meta.get("repository_full_name", "").casefold() != repository_full_name.casefold()
                        )
                    )
                ):
                    continue
                dedup_key = f"{meta.get('repository_name')}:{meta.get('file_path')}:{meta.get('start_line')}"
                if dedup_key in known_keys:
                    continue
                known_keys.add(dedup_key)
                filtered_results.append(item)

        filtered_results.sort(
            key=lambda item: (
                item.get("matched_term_count", 0),
                item.get("score", 0.0),
            ),
            reverse=True,
        )
        filtered_results = filtered_results[:top_k]
        citations = []
        for item in filtered_results:
            meta = item["metadata"]
            snippet = item["content"][:250]
            if len(item["content"]) > 250:
                snippet += "..."
            citations.append(
                SourceCitation(
                    repository_name=meta.get("repository_name", "Unknown"),
                    repository_full_name=meta.get("repository_full_name"),
                    file_path=meta.get("file_path", "Unknown"),
                    source_url=meta.get("source_url", ""),
                    language=meta.get("language", "Code"),
                    snippet=snippet,
                )
            )

        return filtered_results, citations

    def format_context_for_prompt(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved chunks into clean markdown blocks for the LLM prompt.
        """
        if not retrieved_chunks:
            return "No relevant repository files found in the knowledge base."

        formatted_blocks = []
        for idx, item in enumerate(retrieved_chunks, start=1):
            meta = item["metadata"]
            repo = meta.get("repository_full_name") or meta.get("repository_name", "Unknown Repo")
            file_path = meta.get("file_path", "Unknown File")
            lang = meta.get("language", "text")
            start_l = meta.get("start_line", 1)
            end_l = meta.get("end_line", 1)
            content = item["content"]

            block = (
                f"### Document {idx}: [{repo}] {file_path} (Lines {start_l}-{end_l}, Language: {lang})\n"
                f"Source: {meta.get('source_url', '')}\n"
                f"```{lang.lower()}\n{content}\n```"
            )
            formatted_blocks.append(block)

        return "\n\n".join(formatted_blocks)

retriever = GitHubRetriever()
