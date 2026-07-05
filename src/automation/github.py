import subprocess
import json
import time
import base64
from ..utils.logger import setup_logger

logger = setup_logger()


class GitHubSkillsAutomation:
    def __init__(self):
        self.is_authenticated = self._check_auth()

    def _check_auth(self) -> bool:
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True, text=True
            )
            return "Logged in" in result.stdout or "Logged in" in result.stderr
        except Exception:
            return False

    def _run_gh(self, args: list) -> dict:
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True, text=True
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}

    def get_repo_contents(self, repo: str, path: str = "") -> list:
        result = self._run_gh([
            "api", f"repos/{repo}/contents/{path}",
            "--jq", ".[].name"
        ])
        if result["success"]:
            return [f for f in result["stdout"].strip().split("\n") if f]
        return []

    def get_file_content(self, repo: str, path: str) -> str:
        result = self._run_gh([
            "api", f"repos/{repo}/contents/{path}",
            "--jq", ".content"
        ])
        if result["success"] and result["stdout"].strip():
            try:
                return base64.b64decode(result["stdout"].strip()).decode()
            except Exception:
                return result.stdout
        return ""

    def create_file(self, repo: str, path: str, content: str, message: str) -> bool:
        encoded = base64.b64encode(content.encode()).decode()
        result = self._run_gh([
            "api", f"repos/{repo}/contents/{path}",
            "-f", f"message={message}",
            "-f", f"content={encoded}"
        ])
        return result["success"]

    def update_file(self, repo: str, path: str, content: str, message: str, sha: str) -> bool:
        encoded = base64.b64encode(content.encode()).decode()
        result = self._run_gh([
            "api", f"repos/{repo}/contents/{path}",
            "-X", "PUT",
            "-f", f"message={message}",
            "-f", f"content={encoded}",
            "-f", f"sha={sha}"
        ])
        return result["success"]

    def get_file_sha(self, repo: str, path: str) -> str:
        result = self._run_gh([
            "api", f"repos/{repo}/contents/{path}",
            "--jq", ".sha"
        ])
        if result["success"]:
            return result.stdout.strip()
        return ""

    def commit_file(self, repo: str, path: str, content: str) -> bool:
        sha = self.get_file_sha(repo, path)
        if sha:
            return self.update_file(repo, path, content, f"Update {path}", sha)
        else:
            return self.create_file(repo, path, content, f"Add {path}")

    def create_repo_from_template(self, template_owner: str, template_repo: str,
                                   repo_name: str) -> dict:
        logger.info(f"Creating repo from template: {template_owner}/{template_repo}")

        result = self._run_gh([
            "repo", "create", repo_name,
            "--template", f"{template_owner}/{template_repo}",
            "--public", "--clone"
        ])

        if result["success"]:
            logger.info(f"Repo created: {repo_name}")
            return {"success": True, "repo": repo_name, "url": f"https://github.com/{repo_name}"}
        else:
            logger.error(f"Failed to create repo: {result['stderr']}")
            return {"success": False, "error": result["stderr"]}

    def complete_introduction_to_github(self) -> dict:
        import os
        repo = "introduction-to-github-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "introduction-to-github", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        readme_content = self.get_file_content(repo, "README.md")
        logger.info(f"README length: {len(readme_content)}")

        files = self.get_repo_contents(repo)
        logger.info(f"Files in repo: {files}")

        if "profile/README.md" not in files:
            profile_content = f"""# Hello, I'm Faizul Hassan

## About Me
- Learning GitHub skills
- Aspiring developer
- Currently completing GitHub Skills courses

## GitHub Skills Completed
- [x] Introduction to GitHub

## Connect
- GitHub: [@faizulhasson5-sudo](https://github.com/faizulhasson5-sudo)
"""
            self.commit_file(repo, "profile/README.md", profile_content)
            logger.info("Created profile/README.md")

        if "CONTRIBUTING.md" not in files:
            contributing_content = """# Contributing

Thanks for your interest in contributing!

## How to Contribute

1. Fork this repository
2. Create a branch for your changes
3. Make your changes
4. Submit a pull request

## Guidelines

- Follow the existing code style
- Write clear commit messages
- Test your changes before submitting
"""
            self.commit_file(repo, "CONTRIBUTING.md", contributing_content)
            logger.info("Created CONTRIBUTING.md")

        time.sleep(1)
        files_after = self.get_repo_contents(repo)
        logger.info(f"Final files: {files_after}")

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}",
            "files_created": files_after
        }

    def complete_communicating_markdown(self) -> dict:
        repo = "communicating-using-markdown-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "communicating-using-markdown", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        files = self.get_repo_contents(repo)

        if "README.md" not in files or "docs/guide.md" not in files:
            readme = """# Markdown Guide

Welcome to this Markdown practice repository!

## Table of Contents

- [Headers](#headers)
- [Lists](#lists)
- [Links](#links)
- [Code](#code)

## Headers

# H1 Header
## H2 Header
### H3 Header

## Lists

### Unordered List
- Item 1
- Item 2
- Item 3

### Ordered List
1. First item
2. Second item
3. Third item

## Links

[GitHub](https://github.com)

## Code

```python
def hello():
    print("Hello, GitHub!")
```

## Images

![GitHub Logo](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png)
"""
            self.commit_file(repo, "README.md", readme)

            guide = """# Contributing Guide

Thank you for contributing!

## How to Add Content

1. Create a new markdown file
2. Add your content
3. Update the table of contents
4. Submit a pull request

## Markdown Tips

- Use `#` for headers
- Use `-` for lists
- Use `[]()` for links
- Use triple backticks for code blocks
"""
            self.commit_file(repo, "docs/guide.md", guide)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_hello_github_actions(self) -> dict:
        repo = "hello-github-actions-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "hello-github-actions", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        workflow = """name: Hello GitHub Actions

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  hello:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Hello World
      run: echo "Hello from GitHub Actions!"

    - name: Print date
      run: date
"""
        self.commit_file(repo, ".github/workflows/hello.yml", workflow)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_skill(self, skill_name: str) -> dict:
        skill_map = {
            "Introduction to GitHub": self.complete_introduction_to_github,
            "Communicating using Markdown": self.complete_communicating_markdown,
            "Actions: Create your first workflow": self.complete_hello_github_actions,
        }

        if skill_name in skill_map:
            return skill_map[skill_name]()
        else:
            return {"success": False, "error": f"Unknown skill: {skill_name}"}

    def list_user_repos(self) -> list:
        result = self._run_gh(["repo", "list", "--json", "name,url,description"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except Exception:
                return []
        return []
