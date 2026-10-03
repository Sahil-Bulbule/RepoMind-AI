import re
from pathlib import PurePosixPath
from typing import Optional, Set
from ..config import settings


GITHUB_USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$")


IGNORED_DIRECTORIES: Set[str] = {
    ".git", ".github", "node_modules", "venv", ".venv", "env", ".env",
    "__pycache__", "build", "dist", "out", "target", ".next", ".nuxt",
    ".cache", "coverage", ".idea", ".vscode", "vendor", ".turbo",
    ".gradle", "bin", "obj", "site-packages", ".pytest_cache",
    ".mypy_cache", ".eggs", "eggs", "wheels", ".tox"
}


IGNORED_FILES: Set[str] = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "cargo.lock", "composer.lock", "gemfile.lock", "go.sum",
    ".ds_store", "thumbs.db"
}


IGNORED_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".bmp", ".tiff",
    ".mp3", ".wav", ".ogg", ".flac", ".mp4", ".avi", ".mov", ".mkv", ".webm",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".bz2", ".xz",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".iso", ".dat", ".pkl",
    ".pyc", ".pyo", ".pyd", ".class", ".jar", ".war",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".map"
}


EXTENSION_LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".md": "Markdown",
    ".markdown": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".txt": "Plain Text",
    ".go": "Go",
    ".rs": "Rust",
    ".sql": "SQL",
    ".sh": "Shell Script",
    ".bash": "Bash Script",
    ".zsh": "Zsh Script",
    ".php": "PHP",
    ".rb": "Ruby",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".dart": "Dart"
}

def validate_github_username(username: str) -> bool:
    """Validate if the string is a valid GitHub username format."""
    if not username or len(username) > 39:
        return False
    return bool(GITHUB_USERNAME_REGEX.match(username.strip()))

def is_text_file_path(path_str: str) -> bool:
    """
    Check if a relative file path is an eligible source/documentation file.
    Evaluates path components, directory names, lockfiles, minified files,
    and allowed file extensions.
    """
    posix_path = PurePosixPath(path_str.replace("\\", "/"))
    filename = posix_path.name.lower()
    

    parts = [p.lower() for p in posix_path.parts[:-1]]
    for part in parts:
        if part in IGNORED_DIRECTORIES or part.startswith("."):
            return False
            

    if filename in IGNORED_FILES:
        return False
        

    if filename.endswith(".min.js") or filename.endswith(".min.css") or filename.endswith(".bundle.js"):
        return False
        

    suffix = posix_path.suffix.lower()
    if suffix in IGNORED_EXTENSIONS:
        return False
        

    if suffix not in settings.ALLOWED_EXTENSIONS:
        return False
        
    return True

def detect_language(path_str: str) -> str:
    """Determine programming or markup language from file path."""
    suffix = PurePosixPath(path_str).suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(suffix, "Other")

def clean_text_content(content: str) -> str:
    """
    Clean and normalize text content:
    - Remove null bytes
    - Normalize carriage returns
    - Collapse excessive blank lines
    - Truncate excessively long single lines (prevents minified file issues)
    """
    if not content:
        return ""
        

    cleaned = content.replace("\x00", "")
    

    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    
    lines = cleaned.split("\n")
    filtered_lines = []
    
    for line in lines:

        if len(line) > 1500:
            filtered_lines.append(line[:1500] + " ... [line truncated]")
        else:
            filtered_lines.append(line)
            
    result = "\n".join(filtered_lines)
    

    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()
