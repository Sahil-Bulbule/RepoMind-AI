from backend.app.utils.file_filters import (
    validate_github_username,
    is_text_file_path,
    detect_language,
    clean_text_content
)

def test_validate_github_username_valid():
    assert validate_github_username("Sahil-Bulbule") is True
    assert validate_github_username("torvalds") is True
    assert validate_github_username("user-123") is True
    assert validate_github_username("a") is True

def test_validate_github_username_invalid():
    assert validate_github_username("") is False
    assert validate_github_username("-invalid") is False
    assert validate_github_username("invalid-") is False
    assert validate_github_username("user--name") is False
    assert validate_github_username("invalid@user") is False
    assert validate_github_username("user with spaces") is False
    assert validate_github_username("a" * 40) is False

def test_is_text_file_path_allowed():
    assert is_text_file_path("src/app.py") is True
    assert is_text_file_path("components/Button.tsx") is True
    assert is_text_file_path("README.md") is True
    assert is_text_file_path("backend/config.yaml") is True
    assert is_text_file_path("index.html") is True

def test_is_text_file_path_ignored_dirs():
    assert is_text_file_path("node_modules/react/index.js") is False
    assert is_text_file_path(".git/HEAD") is False
    assert is_text_file_path("venv/lib/site.py") is False
    assert is_text_file_path("dist/bundle.js") is False
    assert is_text_file_path(".next/static/chunks/main.js") is False

def test_is_text_file_path_ignored_files():
    assert is_text_file_path("package-lock.json") is False
    assert is_text_file_path("yarn.lock") is False
    assert is_text_file_path("poetry.lock") is False
    assert is_text_file_path("app.min.js") is False
    assert is_text_file_path("logo.png") is False
    assert is_text_file_path("data.pkl") is False
    assert is_text_file_path("app.exe") is False

def test_detect_language():
    assert detect_language("test.py") == "Python"
    assert detect_language("Component.tsx") == "TypeScript (React)"
    assert detect_language("main.go") == "Go"
    assert detect_language("script.sh") == "Shell Script"
    assert detect_language("doc.md") == "Markdown"

def test_clean_text_content():
    raw = "hello\x00world\r\n\r\n\r\nline2"
    cleaned = clean_text_content(raw)
    assert "\x00" not in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
