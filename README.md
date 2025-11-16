# Creator Common Core

Thin toolbox shared by the project and module creators for cloning templates and provisioning GitHub repositories.

## Overview
- Defines `RepoCreationOptions` dataclass reused by wizards and creators
- Provides `clone_template` that strips template git metadata after cloning
- Implements `create_remote_repo` to create/push new GitHub repos via the shared API wrapper
- Offers `TemplateInfo` + `list_templates` helpers for YAML-driven template catalogs

## Features
- **Sanitized cloning** – clones any template repo and removes the `.git` folder to avoid accidental history reuse
- **Repo provisioning** – wraps `GithubApi.create_repo` and `push_initial_commit` with consistent logging and error handling
- **Template catalog parsing** – converts YAML dicts into `TemplateInfo` objects consumed by wizards
- **Utility helpers** – `remove_git_dir` for safe cleanup when reusing existing directories

## Quickstart

```python
from pathlib import Path

from cores.creator_common_core.creator_common_core import (
	RepoCreationOptions,
	clone_template,
	create_remote_repo,
)
from cores.github_api_core.api import GithubApi
from utils.logger_util.logger import Logger

api = GithubApi()
logger = Logger("CreatorCommon")

dest = clone_template(api, "https://github.com/org/python-template", Path("./tmp/template"))

create_remote_repo(
	api=api,
	repo_name="My Service",
	local_path=dest,
	options=RepoCreationOptions(owner="my-org", visibility="private"),
	logger=logger,
)
```

## API

```python
@dataclass
class RepoCreationOptions:
	owner: str
	visibility: str  # "public" | "private"
	repo_url: str | None = None

def clone_template(api: GithubApi, template_url: str, target: pathlib.Path) -> pathlib.Path: ...
def create_remote_repo(
	api: GithubApi,
	repo_name: str,
	local_path: pathlib.Path,
	options: RepoCreationOptions,
	logger: Logger,
) -> None: ...
def remove_git_dir(path: pathlib.Path) -> None: ...

@dataclass
class TemplateInfo:
	name: str
	description: str
	url: str

def list_templates(template_dict: dict[str, dict[str, str]]) -> list[TemplateInfo]: ...
```

## Notes
- `create_remote_repo` sanitizes repo names the same way `GithubApi` does, so spaces become dashes.
- All GitHub operations rely on the CLI; make sure `GithubApi.require_gh()` passes before calling these helpers.
- `list_templates` ignores entries missing a `url`, preventing half-configured templates from leaking into menus.

## Requirements & prerequisites
- GitHub CLI (`gh`) installed and authenticated (enforced by `GithubApi`)
- Python standard library only (plus dependencies pulled in via GithubApi and Logger Utility)

## Troubleshooting
- **Template clone returns False** – the GitHub CLI failed; inspect logs for auth issues or repo typos.
- **Remote repo creation fails silently** – ensure `options.visibility` is either `public` or `private`; other values skip repo creation.
- **list_templates raises ValueError** – verify your YAML resolves to a dict where each value has `description` and `url` keys.

## Module structure

```
cores/creator_common_core/
├─ __init__.py                      # ensures bundled template data is copied into project/data
├─ creator_common_core.py           # shared helpers and dataclasses
├─ .config_template                 # config schema
├─ init.yaml                        # module metadata
└─ README.md                        # this file
```

## See also
- Project Creator Core – consumes these helpers when scaffolding projects
- Module Creator Core – uses the same repo/template utilities
- GitHub API Core – underlying gh CLI wrapper leveraged here