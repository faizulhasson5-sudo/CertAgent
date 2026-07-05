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
        repo = "introduction-to-github-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "introduction-to-github", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        files = self.get_repo_contents(repo)
        logger.info(f"Files in repo: {files}")

        if "profile/README.md" not in files:
            profile_content = (
                "# Hello, I'm Faizul Hassan\n"
                "\n"
                "## About Me\n"
                "- Learning GitHub skills\n"
                "- Aspiring developer\n"
                "- Currently completing GitHub Skills courses\n"
                "\n"
                "## GitHub Skills Completed\n"
                "- [x] Introduction to GitHub\n"
                "\n"
                "## Connect\n"
                "- GitHub: [@faizulhasson5-sudo](https://github.com/faizulhasson5-sudo)"
            )
            self.commit_file(repo, "profile/README.md", profile_content)
            logger.info("Created profile/README.md")

        if "CONTRIBUTING.md" not in files:
            contributing_content = (
                "# Contributing\n"
                "\n"
                "Thanks for your interest in contributing!\n"
                "\n"
                "## How to Contribute\n"
                "\n"
                "1. Fork this repository\n"
                "2. Create a branch for your changes\n"
                "3. Make your changes\n"
                "4. Submit a pull request\n"
                "\n"
                "## Guidelines\n"
                "\n"
                "- Follow the existing code style\n"
                "- Write clear commit messages\n"
                "- Test your changes before submitting"
            )
            self.commit_file(repo, "CONTRIBUTING.md", contributing_content)
            logger.info("Created CONTRIBUTING.md")

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_communicating_markdown(self) -> dict:
        repo = "communicate-using-markdown-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "communicate-using-markdown", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        files = self.get_repo_contents(repo)

        if "index.md" not in files:
            index_content = (
                "# Markdown Practice\n"
                "\n"
                "Welcome to this Markdown practice repository!\n"
                "\n"
                "## Headers\n"
                "\n"
                "# H1 Header\n"
                "## H2 Header\n"
                "### H3 Header\n"
                "\n"
                "## Lists\n"
                "\n"
                "- Item 1\n"
                "- Item 2\n"
                "- Item 3\n"
                "\n"
                "## Links\n"
                "\n"
                "[GitHub](https://github.com)\n"
                "\n"
                "## Task List\n"
                "\n"
                "- [x] Create repository\n"
                "- [x] Add headers\n"
                "- [ ] Add images\n"
                "- [ ] Merge pull request"
            )
            self.commit_file(repo, "index.md", index_content)
            logger.info("Created index.md")

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

        workflow = (
            "name: Hello GitHub Actions\n"
            "\n"
            "on:\n"
            "  push:\n"
            '    branches: ["main"]\n'
            "  pull_request:\n"
            '    branches: ["main"]\n'
            "\n"
            "jobs:\n"
            "  hello:\n"
            "    runs-on: ubuntu-latest\n"
            "\n"
            "    steps:\n"
            "    - name: Checkout code\n"
            "      uses: actions/checkout@v4\n"
            "\n"
            "    - name: Hello World\n"
            '      run: echo "Hello from GitHub Actions!"\n'
            "\n"
            "    - name: Print date\n"
            "      run: date"
        )
        self.commit_file(repo, ".github/workflows/hello.yml", workflow)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_code_with_copilot(self) -> dict:
        repo = "code-with-copilot-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "code-with-copilot", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        index_html = (
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <meta charset="UTF-8">\n'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '    <title>My Web App</title>\n'
            '    <link rel="stylesheet" href="style.css">\n'
            '</head>\n'
            '<body>\n'
            '    <h1>Welcome to My Web App</h1>\n'
            '    <p>This is a practice repository for GitHub Copilot.</p>\n'
            '    <button id="clickMe">Click Me!</button>\n'
            '    <div id="output"></div>\n'
            '    <script src="app.js"></script>\n'
            '</body>\n'
            '</html>'
        )
        self.commit_file(repo, "index.html", index_html)

        style_css = (
            "body {\n"
            "    font-family: Arial, sans-serif;\n"
            "    max-width: 800px;\n"
            "    margin: 0 auto;\n"
            "    padding: 20px;\n"
            "    background-color: #f5f5f5;\n"
            "}\n"
            "\n"
            "h1 {\n"
            "    color: #333;\n"
            "    text-align: center;\n"
            "}\n"
            "\n"
            "button {\n"
            "    background-color: #0066cc;\n"
            "    color: white;\n"
            "    padding: 10px 20px;\n"
            "    border: none;\n"
            "    border-radius: 5px;\n"
            "    cursor: pointer;\n"
            "}\n"
            "\n"
            "button:hover {\n"
            "    background-color: #0055aa;\n"
            "}\n"
            "\n"
            "#output {\n"
            "    margin-top: 20px;\n"
            "    padding: 10px;\n"
            "    background-color: white;\n"
            "    border-radius: 5px;\n"
            "}"
        )
        self.commit_file(repo, "style.css", style_css)

        app_js = (
            "document.getElementById('clickMe').addEventListener('click', function() {\n"
            "    const output = document.getElementById('output');\n"
            "    output.innerHTML = '<p>Hello from GitHub Copilot!</p>';\n"
            "});"
        )
        self.commit_file(repo, "app.js", app_js)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_enable_security_features(self) -> dict:
        repo = "enable-security-features-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "enable-security-features", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        security_md = (
            "# Security Policy\n"
            "\n"
            "## Reporting a Vulnerability\n"
            "\n"
            "If you discover a security vulnerability, please report it responsibly.\n"
            "\n"
            "### How to Report\n"
            "\n"
            "1. Email security@example.com\n"
            "2. Include details about the vulnerability\n"
            "3. Wait for a response before disclosing publicly\n"
            "\n"
            "## Security Best Practices\n"
            "\n"
            "- Keep dependencies updated\n"
            "- Use strong passwords\n"
            "- Enable two-factor authentication\n"
            "- Review code before merging"
        )
        self.commit_file(repo, "SECURITY.md", security_md)

        dependabot_yml = (
            "version: 2\n"
            "updates:\n"
            "  - package-ecosystem: npm\n"
            "    directory: /\n"
            "    schedule:\n"
            "      interval: weekly\n"
            "  - package-ecosystem: github-actions\n"
            "    directory: /\n"
            "    schedule:\n"
            "      interval: weekly"
        )
        self.commit_file(repo, ".github/dependabot.yml", dependabot_yml)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_deploy_to_azure(self) -> dict:
        repo = "deploy-to-azure-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "deploy-to-azure", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        azure_pipelines = (
            "trigger:\n"
            "  branches:\n"
            "    include:\n"
            "      - main\n"
            "\n"
            "pool:\n"
            "  vmImage: ubuntu-latest\n"
            "\n"
            "steps:\n"
            "- task: NodeTool@0\n"
            "  inputs:\n"
            "    versionSpec: 18.x\n"
            "  displayName: Install Node.js\n"
            "\n"
            "- script: |\n"
            "    npm install\n"
            "    npm run build\n"
            "  displayName: Build and Test\n"
            "\n"
            "- task: AzureWebApp@1\n"
            "  inputs:\n"
            "    azureSubscription: Azure Subscription\n"
            "    appType: webApp\n"
            "    appName: my-web-app\n"
            "    package: $(Build.ArtifactStagingDirectory)"
        )
        self.commit_file(repo, "azure-pipelines.yml", azure_pipelines)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_package_management(self) -> dict:
        repo = "package-management-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "package-management", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        package_json = (
            "{\n"
            '  "name": "package-management-practice",\n'
            '  "version": "1.0.0",\n'
            '  "description": "Practice repository for package management",\n'
            '  "main": "index.js",\n'
            '  "scripts": {\n'
            '    "start": "node index.js",\n'
            '    "test": "jest",\n'
            '    "lint": "eslint ."\n'
            "  },\n"
            '  "dependencies": {\n'
            '    "express": "^4.18.2"\n'
            "  },\n"
            '  "devDependencies": {\n'
            '    "jest": "^29.7.0",\n'
            '    "eslint": "^8.56.0"\n'
            "  }\n"
            "}"
        )
        self.commit_file(repo, "package.json", package_json)

        index_js = (
            "const express = require('express');\n"
            "const app = express();\n"
            "const PORT = process.env.PORT || 3000;\n"
            "\n"
            "app.get('/', (req, res) => {\n"
            "    res.send('Hello from Express!');\n"
            "});\n"
            "\n"
            "app.listen(PORT, () => {\n"
            '    console.log(`Server running on port ${PORT}`);\n'
            "});"
        )
        self.commit_file(repo, "index.js", index_js)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_collaboration_pull_requests(self) -> dict:
        repo = "collaboration-with-pull-requests-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "collaboration-with-pull-requests", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        readme = (
            "# Collaboration with Pull Requests\n"
            "\n"
            "Practice repository for learning about pull requests.\n"
            "\n"
            "## How to Contribute\n"
            "\n"
            "1. Fork this repository\n"
            "2. Create a new branch: git checkout -b feature/my-feature\n"
            "3. Make your changes\n"
            "4. Commit your changes: git commit -m 'Add my feature'\n"
            "5. Push to the branch: git push origin feature/my-feature\n"
            "6. Submit a pull request\n"
            "\n"
            "## Pull Request Best Practices\n"
            "\n"
            "- Write clear titles and descriptions\n"
            "- Link related issues\n"
            "- Request reviews from team members\n"
            "- Address feedback promptly"
        )
        self.commit_file(repo, "README.md", readme)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_continuous_integration(self) -> dict:
        repo = "continuous-integration-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "continuous-integration", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        ci_yml = (
            "name: CI\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n"
            "\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "\n"
            "    steps:\n"
            "    - uses: actions/checkout@v4\n"
            "\n"
            "    - name: Setup Node.js\n"
            "      uses: actions/setup-node@v4\n"
            "      with:\n"
            "        node-version: 18\n"
            "\n"
            "    - name: Install dependencies\n"
            "      run: npm ci\n"
            "\n"
            "    - name: Run tests\n"
            "      run: npm test\n"
            "\n"
            "    - name: Run linter\n"
            "      run: npm run lint"
        )
        self.commit_file(repo, ".github/workflows/ci.yml", ci_yml)

        return {
            "success": True,
            "repo": repo,
            "url": f"https://github.com/{repo}"
        }

    def complete_infrastructure_as_code(self) -> dict:
        repo = "infrastructure-as-code-practice"

        existing = self._run_gh(["repo", "view", repo, "--json", "name"])
        if not existing["success"]:
            result = self.create_repo_from_template(
                "skills", "infrastructure-as-code", repo
            )
            if not result["success"]:
                return result
            time.sleep(2)

        main_tf = (
            "terraform {\n"
            "  required_providers {\n"
            "    azurerm = {\n"
            '      source  = "hashicorp/azurerm"\n'
            '      version = "~> 3.0"\n'
            "    }\n"
            "  }\n"
            "}\n"
            "\n"
            'provider "azurerm" {\n'
            "  features {}\n"
            "}\n"
            "\n"
            'resource "azurerm_resource_group" "example" {\n'
            '  name     = "example-resources"\n'
            '  location = "East US"\n'
            "}\n"
            "\n"
            'resource "azurerm_app_service_plan" "example" {\n'
            '  name                = "example-appserviceplan"\n'
            "  location            = azurerm_resource_group.example.location\n"
            "  resource_group_name = azurerm_resource_group.example.name\n"
            "  sku {\n"
            '    tier = "Standard"\n'
            '    size = "S1"\n'
            "  }\n"
            "}\n"
            "\n"
            'resource "azurerm_app_service" "example" {\n'
            '  name                = "example-appservice"\n'
            "  location            = azurerm_resource_group.example.location\n"
            "  resource_group_name = azurerm_resource_group.example.name\n"
            "  app_service_plan_id = azurerm_app_service_plan.example.id\n"
            "}"
        )
        self.commit_file(repo, "main.tf", main_tf)

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
            "Code with Copilot": self.complete_code_with_copilot,
            "Enable Security Features": self.complete_enable_security_features,
            "Deploy to Azure": self.complete_deploy_to_azure,
            "Package Management": self.complete_package_management,
            "Collaboration with Pull Requests": self.complete_collaboration_pull_requests,
            "Continuous Integration": self.complete_continuous_integration,
            "Infrastructure as Code": self.complete_infrastructure_as_code,
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
