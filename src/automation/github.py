import subprocess
import json
import time
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

    def create_repo_from_template(self, template_owner: str, template_repo: str,
                                   repo_name: str) -> dict:
        logger.info(f"Creating repo from template: {template_owner}/{template_repo}")

        result = self._run_gh([
            "repo", "create", repo_name,
            "--template", f"{template_owner}/{template_repo}",
            "--public"
        ])

        if result["success"]:
            logger.info(f"Repo created: {repo_name}")
            return {"success": True, "repo": repo_name, "url": f"https://github.com/{repo_name}"}
        else:
            logger.error(f"Failed to create repo: {result['stderr']}")
            return {"success": False, "error": result["stderr"]}

    def complete_github_skill(self, skill_name: str) -> dict:
        skills = {
            "Introduction to GitHub": {
                "template": "skills/introduction-to-github",
                "steps": [
                    "Create a file called README.md",
                    "Add your name to the file",
                    "Commit and push"
                ]
            },
            "Communicating using Markdown": {
                "template": "skills/communicating-using-markdown",
                "steps": [
                    "Create a markdown file",
                    "Add headers, lists, and links",
                    "Commit and push"
                ]
            },
            "Actions: Create your first workflow": {
                "template": "skills/hello-github-actions",
                "steps": [
                    "Create .github/workflows/ directory",
                    "Add a workflow YAML file",
                    "Commit and push"
                ]
            },
        }

        if skill_name not in skills:
            return {"success": False, "error": "Unknown skill"}

        skill = skills[skill_name]
        template_owner, template_repo = skill["template"].split("/")

        result = self.create_repo_from_template(
            template_owner, template_repo,
            f"{skill_name.lower().replace(' ', '-')}-practice"
        )

        if result["success"]:
            return {
                "success": True,
                "repo": result["repo"],
                "url": result["url"],
                "steps": skill["steps"]
            }
        return result

    def list_user_repos(self) -> list:
        result = self._run_gh(["repo", "list", "--json", "name,url,description"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except Exception:
                return []
        return []

    def push_files_to_repo(self, repo: str, files: dict) -> dict:
        for filename, content in files.items():
            result = self._run_gh([
                "api", f"repos/{repo}/contents/{filename}",
                "-f", f"message=Add {filename}",
                "-f", f"content={content}"
            ])
            if not result["success"]:
                return {"success": False, "error": result["stderr"]}
        return {"success": True}

    def get_repo_contents(self, repo: str, path: str = "") -> list:
        result = self._run_gh([
            "api", f"repos/{repo}/contents/{path}",
            "--jq", ".[].name"
        ])
        if result["success"]:
            return result["stdout"].strip().split("\n")
        return []
