import hashlib
import logging
import re
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings
from .embeddings import embedding_service

logger = logging.getLogger("ask_my_github")

class VectorStore:
    _SEARCH_STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "can", "could",
        "code", "codes", "did", "do", "does", "for", "from", "has", "have",
        "how", "i", "implementation", "implemented", "implementing", "in", "is",
        "it", "me", "of", "on", "or", "please", "project", "projects", "repo",
        "repos", "repository", "repositories", "search", "show", "source", "tell",
        "that", "the", "this", "to", "use", "used", "using", "what", "when",
        "where", "which", "who", "why", "with", "would",
    }

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection_name = "ask_my_github_knowledge"
        self._repository_metadata_ready = set()
        self._get_or_create_collection()

    @staticmethod
    def _build_where_clause(
        username: str,
        repository_filter: Optional[str] = None,
        repository_id: Optional[int] = None,
        repository_full_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        filters = [{"github_username": {"$eq": username.strip().lower()}}]
        if repository_filter and repository_filter.strip():
            filters.append({"repository_name": {"$eq": repository_filter.strip()}})
        if repository_id is not None:
            filters.append({"repository_id": {"$eq": str(repository_id)}})
        if repository_full_name and repository_full_name.strip():
            filters.append({"repository_full_name": {"$eq": repository_full_name.strip().lower()}})
        return filters[0] if len(filters) == 1 else {"$and": filters}

    def _get_or_create_collection(self):
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Ask My GitHub Knowledge Chunks"}
            )
        except Exception as e:
            logger.error("Error accessing ChromaDB collection (%s)", type(e).__name__)
            raise

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Batch adds processed chunks to ChromaDB with generated embeddings and strict metadata.
        """
        if not chunks:
            return

        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            texts = [c["chunk_text"] for c in batch]
            metadatas = [c["metadata"] for c in batch]
            

            ids = []
            for c in batch:
                meta = c["metadata"]
                id_raw = f"{meta['github_username']}_{meta['repository_name']}_{meta['file_path']}_{meta['chunk_index']}"
                chunk_id = hashlib.sha256(id_raw.encode("utf-8")).hexdigest()[:24]
                ids.append(chunk_id)


            embeddings = embedding_service.get_embeddings(texts)

            self.collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )

    def delete_user_knowledge(self, username: str):
        """
        Purges all chunks associated with a GitHub username.
        Used for cache refresh or profile reset.
        """
        canon_user = username.strip().lower()
        try:
            self.collection.delete(
                where={"github_username": {"$eq": canon_user}}
            )
            logger.info(f"Deleted existing knowledge vectors for {canon_user}")
        except Exception as e:
            logger.warning(
                "Error deleting knowledge for %s (%s)",
                canon_user,
                type(e).__name__,
            )

    def delete_repository_knowledge(self, username: str, repository_name: str):
        canon_user = username.strip().lower()
        try:
            self.collection.delete(
                where=self._build_where_clause(
                    canon_user,
                    repository_filter=repository_name,
                )
            )
        except Exception as e:
            logger.error(
                "Error deleting vectors for %s/%s (%s)",
                canon_user,
                repository_name,
                type(e).__name__,
            )
            raise RuntimeError("Repository data cleanup failed.") from e

    def ensure_repository_metadata(
        self,
        username: str,
        repository_name: str,
        repository_id: int,
        repository_full_name: str,
        repository_url: str,
    ) -> None:
        """Backfill stable identity fields on chunks created before repository scoping."""
        canon_user = username.strip().lower()
        cache_key = (canon_user, repository_id)
        if cache_key in self._repository_metadata_ready:
            return
        where = self._build_where_clause(canon_user, repository_filter=repository_name)
        try:
            records = self.collection.get(where=where, include=["metadatas"])
            ids = records.get("ids", [])
            metadatas = records.get("metadatas", [])
            updates = []
            for index, metadata in enumerate(metadatas):
                updated = dict(metadata)
                identity = {
                    "repository_id": str(repository_id),
                    "repository_full_name": repository_full_name,
                    "repository_url": repository_url,
                }
                if any(updated.get(key) != value for key, value in identity.items()):
                    updated.update(identity)
                    updates.append((updated, index))
            if ids and updates:
                changed_ids = []
                changed_metadata = []
                for metadata, index in updates:
                    changed_ids.append(ids[index])
                    changed_metadata.append(metadata)
                self.collection.update(ids=changed_ids, metadatas=changed_metadata)
            self._repository_metadata_ready.add(cache_key)
        except Exception:
            logger.error(
                "Failed to ensure Chroma identity metadata for %s/%s",
                canon_user,
                repository_name,
            )
            raise

    def query(
        self,
        username: str,
        query_text: str,
        repository_filter: Optional[str] = None,
        repository_id: Optional[int] = None,
        repository_full_name: Optional[str] = None,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Semantic similarity query with MANDATORY user-isolation filtering.
        Never retrieves chunks from another user.
        """
        canon_user = username.strip().lower()
        query_embedding = embedding_service.get_query_embedding(query_text)


        where_clause = self._build_where_clause(
            canon_user,
            repository_filter=repository_filter,
            repository_id=repository_id,
            repository_full_name=repository_full_name,
        )

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logger.exception("ChromaDB query failed for %s", canon_user)
            raise RuntimeError("Repository search is temporarily unavailable.") from e

        retrieved_items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else []
            distances = results["distances"][0] if "distances" in results else []

            for doc, meta, dist in zip(docs, metas, distances):


                score = round(max(0.0, 1.0 - (dist / 2.0 if dist is not None else 0.5)), 3)
                retrieved_items.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "score": score
                })

        return retrieved_items

    @classmethod
    def _search_terms(cls, query_text: str) -> List[str]:
        """Tokenize search text, including camel-case identifiers, for exact matching."""
        split_identifiers = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", query_text)
        tokens = re.findall(r"[a-zA-Z0-9]+", split_identifiers.casefold())
        terms = []
        for token in tokens:
            if token in cls._SEARCH_STOP_WORDS:
                continue
            if token.endswith("ies") and len(token) > 4:
                token = f"{token[:-3]}y"
            elif token.endswith("s") and not token.endswith(("ss", "us", "is")) and len(token) > 4:
                token = token[:-1]
            if token not in terms:
                terms.append(token)
        return terms

    def lexical_search(
        self,
        username: str,
        query_text: str,
        repository_filter: Optional[str] = None,
        top_k: int = 500,
    ) -> List[Dict[str, Any]]:
        """Return only indexed chunks containing every meaningful search term."""
        terms = self._search_terms(query_text)
        if not terms:
            return []

        where_clause = self._build_where_clause(
            username,
            repository_filter=repository_filter,
        )
        matching_items = []
        offset = 0
        page_size = 500
        try:
            while True:
                records = self.collection.get(
                    where=where_clause,
                    include=["documents", "metadatas"],
                    limit=page_size,
                    offset=offset,
                )
                ids = records.get("ids", [])
                documents = records.get("documents", [])
                metadatas = records.get("metadatas", [])
                for record_id, document, metadata in zip(ids, documents, metadatas):
                    searchable_text = " ".join(
                        str(value or "")
                        for value in (
                            document,
                            metadata.get("file_path"),
                        )
                    )
                    split_identifiers = re.sub(
                        r"([a-z0-9])([A-Z])", r"\1 \2", searchable_text
                    )
                    normalized_indexed_terms = set(self._search_terms(split_identifiers))
                    if not all(term in normalized_indexed_terms for term in terms):
                        continue

                    content = document or ""
                    occurrences = sum(
                        len(re.findall(rf"(?<![a-zA-Z0-9]){re.escape(term)}(?![a-zA-Z0-9])", searchable_text.casefold()))
                        for term in terms
                    )
                    score = round(0.7 + 0.3 * min(1.0, occurrences / (len(terms) * 3)), 3)
                    matching_items.append({
                        "id": record_id,
                        "content": content,
                        "metadata": metadata,
                        "distance": None,
                        "score": score,
                    })

                if len(ids) < page_size:
                    break
                offset += len(ids)
        except Exception:
            logger.error("Exact code search failed for %s", username)
            raise

        matching_items.sort(
            key=lambda item: (
                item["score"],
                item["metadata"].get("repository_name", "").casefold(),
                item["metadata"].get("file_path", "").casefold(),
            ),
            reverse=True,
        )
        return matching_items[:top_k]

    def keyword_query(
        self,
        username: str,
        query_text: str,
        repository_filter: Optional[str] = None,
        repository_id: Optional[int] = None,
        repository_full_name: Optional[str] = None,
        top_k: int = 24,
    ) -> List[Dict[str, Any]]:
        """Find indexed chunks with meaningful query terms inside the requested scope."""
        terms = self._search_terms(query_text)
        if not terms:
            return []

        where_clause = self._build_where_clause(
            username,
            repository_filter=repository_filter,
            repository_id=repository_id,
            repository_full_name=repository_full_name,
        )
        ranked = []
        offset = 0
        page_size = 500
        try:
            while True:
                records = self.collection.get(
                    where=where_clause,
                    include=["documents", "metadatas"],
                    limit=page_size,
                    offset=offset,
                )
                ids = records.get("ids", [])
                documents = records.get("documents", [])
                metadatas = records.get("metadatas", [])
                for doc_id, document, metadata in zip(ids, documents, metadatas):
                    searchable_text = " ".join(
                        str(value or "")
                        for value in (document, metadata.get("file_path"))
                    )
                    normalized_indexed_terms = set(self._search_terms(
                        re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", searchable_text)
                    ))
                    matched_terms = [term for term in terms if term in normalized_indexed_terms]
                    if not matched_terms:
                        continue
                    score = 0.3 + 0.7 * len(matched_terms) / len(terms)
                    ranked.append({
                        "id": doc_id,
                        "content": document,
                        "metadata": metadata,
                        "distance": None,
                        "score": round(score, 3),
                        "matched_term_count": len(matched_terms),
                    })
                if len(ids) < page_size:
                    break
                offset += len(ids)
        except Exception:
            logger.error("Keyword retrieval failed for %s", username)
            raise

        ranked.sort(
            key=lambda item: (
                item["matched_term_count"],
                item["score"],
                item["metadata"].get("file_path", "").casefold(),
            ),
            reverse=True,
        )
        return ranked[:top_k]

    def count(self) -> int:
        """Returns total vector count in the collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

vector_store = VectorStore()
