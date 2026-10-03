import re
from typing import List, Dict, Any, Optional
from ..config import settings
from ..utils.file_filters import detect_language


SEPARATORS_BY_EXT = {
    ".py": ["\nclass ", "\ndef ", "\nasync def ", "\n\n", "\n", " ", ""],
    ".js": ["\nclass ", "\nfunction ", "\nexport ", "\nconst ", "\nlet ", "\nvar ", "\n\n", "\n", " ", ""],
    ".jsx": ["\nfunction ", "\nconst ", "\nexport default ", "\nclass ", "\n\n", "\n", " ", ""],
    ".ts": ["\ninterface ", "\ntype ", "\nclass ", "\nfunction ", "\nexport ", "\n\n", "\n", " ", ""],
    ".tsx": ["\ninterface ", "\ntype ", "\nfunction ", "\nconst ", "\nexport default ", "\n\n", "\n", " ", ""],
    ".java": ["\npublic class ", "\nclass ", "\npublic ", "\nprivate ", "\nprotected ", "\n\n", "\n", " ", ""],
    ".cpp": ["\nclass ", "\nstruct ", "\nvoid ", "\nint ", "\n\n", "\n", " ", ""],
    ".c": ["\nvoid ", "\nint ", "\nstruct ", "\n\n", "\n", " ", ""],
    ".go": ["\nfunc ", "\ntype ", "\npackage ", "\n\n", "\n", " ", ""],
    ".rs": ["\nfn ", "\npub fn ", "\nimpl ", "\nstruct ", "\nenum ", "\n\n", "\n", " ", ""],
    ".md": ["\n# ", "\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
}

DEFAULT_SEPARATORS = ["\n\n", "\n", ";\n", ". ", " ", ""]


class CodeTextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def _split_text_with_separators(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using the given list of separators.
        """
        final_chunks = []
        separator = separators[-1]
        new_separators = []
        
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)

        good_splits = []
        for s in splits:
            if not s.strip():
                continue
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    other_info = self._split_text_with_separators(s, new_separators)
                    good_splits.extend(other_info)
                else:

                    for start in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        good_splits.append(s[start:start + self.chunk_size])


        merged = []
        current = ""
        for piece in good_splits:
            if not current:
                current = piece
            elif len(current) + len(separator) + len(piece) <= self.chunk_size:
                current = f"{current}{separator}{piece}"
            else:
                merged.append(current.strip())

                overlap_text = current[-self.chunk_overlap:] if len(current) > self.chunk_overlap else current
                current = f"{overlap_text}{separator}{piece}"

        if current and current.strip():
            merged.append(current.strip())

        return merged

    def chunk_file(
        self,
        username: str,
        repo_name: str,
        repo_url: str,
        file_path: str,
        branch: str,
        content: str,
        repository_full_name: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Splits a file's content into rich chunks annotated with metadata and line numbers.
        """
        if not content or not content.strip():
            return []

        ext = "." + file_path.split(".")[-1].lower() if "." in file_path else ""
        separators = SEPARATORS_BY_EXT.get(ext, DEFAULT_SEPARATORS)
        language = detect_language(file_path)

        raw_chunks = self._split_text_with_separators(content, separators)
        if not raw_chunks:
            return []


        lines = content.splitlines(keepends=True)
        line_offsets = []
        current_offset = 0
        for line in lines:
            line_offsets.append(current_offset)
            current_offset += len(line)

        def offset_to_line(char_idx: int) -> int:
            for l_num, off in enumerate(line_offsets, start=1):
                if char_idx <= off:
                    return max(1, l_num)
            return len(lines)

        processed_chunks = []
        total = len(raw_chunks)
        search_cursor = 0

        for idx, text in enumerate(raw_chunks):

            pos = content.find(text[:min(50, len(text))], search_cursor)
            if pos != -1:
                start_line = offset_to_line(pos)
                end_line = offset_to_line(pos + len(text))
                search_cursor = pos + 1
            else:
                start_line = 1
                end_line = max(1, len(lines))


            source_url = f"{repo_url}/blob/{branch}/{file_path}#L{start_line}-L{end_line}"

            processed_chunks.append({
                "chunk_text": text,
                "metadata": {
                    "github_username": username.lower(),
                    "repository_name": repo_name,
                    "repository_full_name": (repository_full_name or f"{username}/{repo_name}").lower(),
                    "repository_id": str(repository_id or f"{username.lower()}/{repo_name.lower()}"),
                    "repository_url": repo_url,
                    "file_path": file_path,
                    "file_extension": ext,
                    "language": language,
                    "branch": branch,
                    "source_url": source_url,
                    "chunk_index": idx,
                    "total_chunks": total,
                    "start_line": start_line,
                    "end_line": end_line
                }
            })

        return processed_chunks
