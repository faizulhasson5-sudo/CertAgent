from typing import List, Dict
from .base import BaseDiscovery


class GitHubSkillsDiscovery(BaseDiscovery):
    COURSES = [
        {
            "name": "Introduction to GitHub",
            "url": "https://github.com/skills/introduction-to-github",
            "description": "Learn GitHub fundamentals",
            "badge": "github-skills"
        },
        {
            "name": "Communicating using Markdown",
            "url": "https://github.com/skills/communicating-using-markdown",
            "description": "Master Markdown for documentation",
            "badge": "github-skills"
        },
        {
            "name": "Actions: Create your first workflow",
            "url": "https://github.com/skills/hello-github-actions",
            "description": "Learn GitHub Actions basics",
            "badge": "github-skills"
        },
        {
            "name": "Code with Copilot",
            "url": "https://github.com/skills/code-with-copilot",
            "description": "AI-powered coding with Copilot",
            "badge": "github-skills"
        },
        {
            "name": "Enable Security Features",
            "url": "https://github.com/skills/security-with-github",
            "description": "GitHub security best practices",
            "badge": "github-skills"
        },
        {
            "name": "Deploy to Azure",
            "url": "https://github.com/skills/deploy-to-azure",
            "description": "Deploy apps to Azure",
            "badge": "github-skills"
        },
        {
            "name": "Package Management",
            "url": "https://github.com/skills/package-management",
            "description": "Manage packages with GitHub",
            "badge": "github-skills"
        },
        {
            "name": "Collaboration with Pull Requests",
            "url": "https://github.com/skills/pull-requests",
            "description": "Master pull request workflow",
            "badge": "github-skills"
        },
        {
            "name": "Continuous Integration",
            "url": "https://github.com/skills/continuous-integration",
            "description": "CI/CD with GitHub Actions",
            "badge": "github-skills"
        },
        {
            "name": "Infrastructure as Code",
            "url": "https://github.com/skills/infrastructure-as-code",
            "description": "IaC with GitHub",
            "badge": "github-skills"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for course in self.COURSES:
            courses.append({
                "platform": "github_skills",
                "name": course["name"],
                "url": course["url"],
                "description": course["description"],
                "badge": course["badge"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
