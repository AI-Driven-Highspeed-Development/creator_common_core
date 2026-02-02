from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import shutil

from github_api_core import GithubApi
from exceptions_core import ADHDError


@dataclass
class RepoCreationOptions:
    owner: str
    visibility: str  # "public" or "private"
    repo_url: Optional[str] = None


def remove_git_dir(path: Path) -> None:
    """Remove a .git directory if present under the given path."""
    git_dir = path / ".git"
    if git_dir.exists() and git_dir.is_dir():
        shutil.rmtree(git_dir)


def clone_template(api: GithubApi, template_url: str, target: Path) -> Path:
    """Clone a template repository into target and strip its VCS metadata.

    Returns the resolved destination path.
    """
    repo = api.repo(template_url)
    dest = repo.clone_repo(str(target))
    if not dest:
        raise ADHDError(f"Failed to clone template from {template_url} to {target}")
    dest_path = Path(dest).resolve()
    remove_git_dir(dest_path)
    return dest_path


def create_remote_repo(
    repo_name: str,
    local_path: Path,
    options: RepoCreationOptions,
    logger,
) -> None:
    """Create a remote repository and push the initial commit.
    
    Creates a GithubApi instance internally to handle the remote repo creation.
    """
    if not options:
        return

    api = GithubApi()
    
    try:
        # Sanitize repo name using the same rules as GithubApi helpers
        sanitized_repo_name = GithubApi.sanitize_repo_name(repo_name)
        if not sanitized_repo_name:
            raise ValueError("Repository name cannot be empty.")

        is_private = options.visibility.lower() == "private"
        if not api.create_repo(options.owner, sanitized_repo_name, private=is_private):
            raise ADHDError(f"Failed to create remote repository {options.owner}/{sanitized_repo_name}")

        api.push_initial_commit(
            local_path,
            options.owner,
            sanitized_repo_name,
            branch="main",
            message="Initial commit",
        )
        logger.info(f"Remote repository created: {options.owner}/{sanitized_repo_name}")

    except Exception as exc:
        logger.error(f"Remote repository creation failed: {exc}")
        # Re-raise as ADHDError to classify as application/service error
        raise ADHDError(f"Remote repository creation failed: {exc}") from exc


__all__ = [
    "RepoCreationOptions",
    "clone_template",
    "remove_git_dir",
    "create_remote_repo",
]

# ---------------- Template listing utilities (generic) ----------------

@dataclass
class TemplateInfo:
    name: str
    description: str
    url: str

def list_templates(template_dict: dict) -> list[TemplateInfo]:
    """Extract template entries from a dict.

    Expected schema:
      <template_name>:
        description: str
        url: str
    """
    if not isinstance(template_dict, dict):
        raise ValueError("templates YAML must be a mapping of template name -> {description, url}")
    out: list[TemplateInfo] = []
    for name, value in template_dict.items():
        if not isinstance(value, dict):
            raise ValueError("Each template entry must be a mapping with 'description' and 'url'")
        desc = str(value.get("description", ""))
        url = str(value.get("url", ""))
        if url:
            out.append(TemplateInfo(name=name, description=desc, url=url))
    return out

__all__ += ["TemplateInfo", "list_templates"]


# ---------------- String utilities ----------------

import re

def to_snake_case(value: str) -> str:
    """Convert a string to snake_case, removing non-alphanumeric characters."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower() or "unnamed"

__all__ += ["to_snake_case"]