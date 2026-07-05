from typing import List, Dict
from .base import BaseDiscovery


class MicrosoftLearnDiscovery(BaseDiscovery):
    PATHS = [
        {
            "name": "Azure Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/",
            "description": "Describe cloud concepts, core services, security, governance",
            "badge": "azure-fundamentals"
        },
        {
            "name": "Azure AI Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/get-started-with-artificial-intelligence-on-azure/",
            "description": "AI concepts and Azure AI services",
            "badge": "azure-ai"
        },
        {
            "name": "Power Platform Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/power-platform-fundamentals/",
            "description": "Business value of Power Platform",
            "badge": "power-platform"
        },
        {
            "name": "Microsoft 365 Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/m365-fundamentals/",
            "description": "Microsoft 365 cloud services",
            "badge": "m365"
        },
        {
            "name": "Security, Compliance, Identity Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/security-compliance-identity-fundamentals/",
            "description": "Security concepts in Azure",
            "badge": "security"
        },
        {
            "name": "Data Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/data-fundamentals/",
            "description": "Core data concepts in Azure",
            "badge": "data"
        },
        {
            "name": "Digital Transformation with Azure",
            "url": "https://learn.microsoft.com/en-us/training/paths/azure-digital-transformation-fundamentals/",
            "description": "Digital transformation strategies",
            "badge": "digital"
        },
        {
            "name": "JavaScript for Beginners",
            "url": "https://learn.microsoft.com/en-us/training/paths/intro-to-javascript/",
            "description": "JavaScript fundamentals",
            "badge": "javascript"
        },
        {
            "name": "Python for Beginners",
            "url": "https://learn.microsoft.com/en-us/training/paths/beginner-python/",
            "description": "Python programming basics",
            "badge": "python"
        },
        {
            "name": "HTML and CSS Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/html-css-fundamentals/",
            "description": "Web development basics",
            "badge": "web"
        },
        {
            "name": "GitHub Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/github-fundamentals/",
            "description": "Version control with GitHub",
            "badge": "github"
        },
        {
            "name": "DevOps Fundamentals",
            "url": "https://learn.microsoft.com/en-us/training/paths/devops-foundations/",
            "description": "DevOps practices and tools",
            "badge": "devops"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for path in self.PATHS:
            courses.append({
                "platform": "microsoft_learn",
                "name": path["name"],
                "url": path["url"],
                "description": path["description"],
                "badge": path["badge"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
