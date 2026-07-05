from typing import List, Dict
from .base import BaseDiscovery


class KaggleDiscovery(BaseDiscovery):
    COURSES = [
        {"slug": "intro-to-machine-learning", "name": "Intro to Machine Learning"},
        {"slug": "intermediate-machine-learning", "name": "Intermediate Machine Learning"},
        {"slug": "intro-to-deep-learning", "name": "Intro to Deep Learning"},
        {"slug": "computer-vision", "name": "Computer Vision"},
        {"slug": "feature-engineering", "name": "Feature Engineering"},
        {"slug": "intro-to-sql", "name": "Intro to SQL"},
        {"slug": "advanced-sql", "name": "Advanced SQL"},
        {"slug": "intro-to-ai-ethics", "name": "Intro to AI Ethics"},
        {"slug": "data-visualization", "name": "Data Visualization"},
        {"slug": "intro-to-programming", "name": "Intro to Programming"},
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for course in self.COURSES:
            courses.append({
                "platform": "kaggle",
                "name": course["name"],
                "url": f"https://www.kaggle.com/learn/{course['slug']}",
                "description": f"Kaggle micro-course: {course['name']}"
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
