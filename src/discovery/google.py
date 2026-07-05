from typing import List, Dict
from .base import BaseDiscovery


class GoogleDiscovery(BaseDiscovery):
    COURSES = [
        {
            "name": "Fundamentals of Digital Marketing",
            "url": "https://learndigital.withgoogle.com/digitalgarage/course/digital-marketing",
            "description": "Google's free digital marketing course with certificate"
        },
        {
            "name": "Google AI Essentials",
            "url": "https://learndigital.withgoogle.com/ai-essentials",
            "description": "Learn AI fundamentals from Google"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for course in self.COURSES:
            courses.append({
                "platform": "google",
                "name": course["name"],
                "url": course["url"],
                "description": course["description"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
