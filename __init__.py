"""creator_common_core - Common utilities for project/module creation.

Provides RepoCreationOptions, QuestionaryCore, and helper functions for template handling.
"""

from .creator_common_core import (
    RepoCreationOptions,
    TemplateInfo,
    list_templates,
    remove_git_dir,
    clone_template,
    create_remote_repo,
    to_snake_case,
    QuestionaryCore,
)

__all__ = [
    "RepoCreationOptions",
    "TemplateInfo",
    "list_templates",
    "remove_git_dir",
    "clone_template",
    "create_remote_repo",
    "to_snake_case",
    "QuestionaryCore",
]