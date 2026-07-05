from typing import List, Dict
from .base import BaseDiscovery


class GoogleCloudDiscovery(BaseDiscovery):
    COURSES = [
        {
            "name": "Google Cloud Fundamentals: Core Infrastructure",
            "url": "https://www.cloudskillsboost.google/course_templates/94",
            "description": "Core GCP services and infrastructure",
            "badge": "gcp-core"
        },
        {
            "name": "Google Cloud Fundamentals: Big Data & ML",
            "url": "https://www.cloudskillsboost.google/course_templates/95",
            "description": "Big data and ML on GCP",
            "badge": "gcp-bigdata"
        },
        {
            "name": "Introduction to Generative AI",
            "url": "https://www.cloudskillsboost.google/course_templates/1389",
            "description": "Generative AI concepts",
            "badge": "gcp-genai"
        },
        {
            "name": "Introduction to Responsible AI",
            "url": "https://www.cloudskillsboost.google/course_templates/1376",
            "description": "Responsible AI principles",
            "badge": "gcp-responsible-ai"
        },
        {
            "name": "Gemini for Google Cloud",
            "url": "https://www.cloudskillsboost.google/course_templates/1464",
            "description": "Using Gemini in GCP",
            "badge": "gcp-gemini"
        },
        {
            "name": "Google Cloud Computing Foundations",
            "url": "https://www.cloudskillsboost.google/course_templates/1454",
            "description": "Cloud computing basics",
            "badge": "gcp-foundations"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for course in self.COURSES:
            courses.append({
                "platform": "google_cloud",
                "name": course["name"],
                "url": course["url"],
                "description": course["description"],
                "badge": course["badge"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
