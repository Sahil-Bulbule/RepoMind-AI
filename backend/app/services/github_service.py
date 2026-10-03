import logging
import httpx
from typing import Dict, Any, List, Optional, Tuple
from ..config import settings
from ..utils.file_filters import (
    validate_github_username,
    is_text_file_path,
    detect_language,
    clean_text_content
)

logger = logging.getLogger("ask_my_github")

class GitHubAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AskMyGitHub-RAG-App/1.0",
        }
        if self.token and self.token.strip():
            self.headers["Authorization"] = f"Bearer {self.token.strip()}"

    def _check_rate_limit(self, response: httpx.Response):
        """Inspect GitHub rate limit headers and raise user-friendly error if exceeded."""
        if response.status_code == 403 and "rate limit" in response.text.lower():
            reset_time = response.headers.get("x-ratelimit-reset", "")
            raise GitHubAPIError(
                "GitHub API rate limit exceeded. Provide a personal GITHUB_TOKEN in .env to enjoy 5,000 requests/hour.",
                status_code=429
            )

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch public profile for a GitHub user."""
        if not validate_github_username(username):
            raise GitHubAPIError(f"Invalid GitHub username format: '{username}'.", status_code=400)

        url = f"{settings.GITHUB_API_BASE}/users/{username}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.get(url, headers=self.headers)
            except httpx.RequestError as e:
                raise GitHubAPIError("Network error contacting GitHub.", status_code=502) from e

            self._check_rate_limit(res)

            if res.status_code == 404:
                raise GitHubAPIError(f"GitHub user '{username}' was not found.", status_code=404)
            if res.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API returned status {res.status_code}.",
                    status_code=res.status_code,
                )

            data = res.json()
            return {
                "username": data.get("login"),
                "name": data.get("name") or data.get("login"),
                "avatar_url": data.get("avatar_url"),
                "bio": data.get("bio") or "",
                "public_repos": data.get("public_repos", 0),
                "html_url": data.get("html_url"),
            }

    async def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Fetch every public repository owned by a user, sorted by latest push."""
        url = f"{settings.GITHUB_API_BASE}/users/{username}/repos"
        params = {"per_page": 100, "sort": "pushed", "direction": "desc", "type": "owner"}
        repositories = []

        async with httpx.AsyncClient(timeout=20.0) as client:
            page = 1
            try:
                while True:
                    res = await client.get(
                        url,
                        headers=self.headers,
                        params={**params, "page": page},
                    )
                    self._check_rate_limit(res)

                    if res.status_code != 200:
                        raise GitHubAPIError(
                            f"GitHub repository request failed with status {res.status_code}.",
                            status_code=res.status_code,
                        )

                    page_repositories = res.json()
                    repositories.extend(page_repositories)
                    if len(page_repositories) < params["per_page"]:
                        break
                    page += 1
            except httpx.RequestError as e:
                raise GitHubAPIError("Network error fetching repositories.", status_code=502) from e

        return [repository for repository in repositories if not repository.get("private", False)]

    async def get_repository_tree(self, owner: str, repo: str, default_branch: str) -> List[Dict[str, Any]]:
        """
        Fetch the entire file tree of a repository recursively in a single API call.
        Returns list of tree items.
        """
        url = f"{settings.GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                res = await client.get(url, headers=self.headers)
            except httpx.RequestError as e:
                logger.warning("Error fetching tree for %s (%s)", repo, type(e).__name__)
                return []

            self._check_rate_limit(res)
            if res.status_code != 200:
                logger.warning("Tree API failed for %s (status %s)", repo, res.status_code)
                return []

            data = res.json()
            return data.get("tree", [])

    async def fetch_file_content(self, owner: str, repo: str, branch: str, path: str) -> Optional[str]:
        """
        Download raw file content from GitHub using raw URL with auth headers.
        """
        url = f"{settings.GITHUB_RAW_BASE}/{owner}/{repo}/{branch}/{path}"
        headers = {}
        if self.token and self.token.strip():
            headers["Authorization"] = f"token {self.token.strip()}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    return clean_text_content(res.text)

                api_url = f"{settings.GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
                res_api = await client.get(
                    api_url,
                    headers={**self.headers, "Accept": "application/vnd.github.v3.raw"}
                )
                if res_api.status_code == 200:
                    return clean_text_content(res_api.text)
            except Exception as e:
                logger.warning(
                    "Failed to fetch content for %s/%s (%s)",
                    repo,
                    path,
                    type(e).__name__,
                )
                return None

        return None

    async def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """Fetch README text if available."""
        url = f"{settings.GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(
                    url,
                    headers={**self.headers, "Accept": "application/vnd.github.v3.raw"}
                )
                if res.status_code == 200:
                    return clean_text_content(res.text)
            except Exception:
                pass
        return None

    def detect_technologies_from_files(
        self,
        repo_languages: List[str],
        file_paths: List[str],
        readme_text: str = ""
    ) -> List[str]:
        """
        Extract high-confidence technologies used across the repositories.
        """
        tech_set = set()
        for lang in repo_languages:
            if lang and lang.strip():
                tech_set.add(lang.strip())

        lowered_paths = " ".join([p.lower() for p in file_paths])
        lowered_readme = (readme_text or "").lower()


        tech_indicators = {
            "React": ["react", "jsx", "tsx", "@types/react"],
            "Next.js": ["next.config", "next", "pages/_app", "app/layout"],
            "Vue": ["vue", ".vue", "nuxt"],
            "Angular": ["angular", "@angular"],
            "FastAPI": ["fastapi", "uvicorn"],
            "Flask": ["flask", "wsgi.py"],
            "Django": ["django", "manage.py"],
            "Express": ["express", "app.use("],
            "NestJS": ["@nestjs"],
            "Node.js": ["package.json", "node_modules"],
            "Tailwind CSS": ["tailwind.config", "tailwind"],
            "TensorFlow": ["tensorflow", "tf.keras"],
            "PyTorch": ["torch", "torchvision"],
            "Scikit-Learn": ["sklearn", "scikit-learn"],
            "MongoDB": ["mongodb", "pymongo", "mongoose"],
            "PostgreSQL": ["postgresql", "psycopg", "postgres"],
            "SQLite": ["sqlite", "sqlite3"],
            "Redis": ["redis"],
            "Docker": ["dockerfile", "docker-compose"],
            "Kubernetes": ["k8s", "kubernetes", "helm"],
            "GraphQL": ["graphql", "apollo"],
            "Spring Boot": ["springboot", "spring-boot", "pom.xml"],
        }

        combined_text = f"{lowered_paths} {lowered_readme}"
        for tech, patterns in tech_indicators.items():
            for pat in patterns:
                if pat in combined_text:
                    tech_set.add(tech)
                    break

        return sorted(list(tech_set))
