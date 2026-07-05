from typing import List, Dict
from .base import BaseDiscovery


class HubSpotDiscovery(BaseDiscovery):
    CERTIFICATIONS = [
        {
            "name": "Inbound Marketing",
            "url": "https://academy.hubspot.com/courses/inbound-marketing",
            "description": "Learn inbound marketing methodology"
        },
        {
            "name": "Content Marketing",
            "url": "https://academy.hubspot.com/courses/content-marketing",
            "description": "Master content marketing strategy"
        },
        {
            "name": "Email Marketing",
            "url": "https://academy.hubspot.com/courses/email-marketing",
            "description": "Learn email marketing best practices"
        },
        {
            "name": "Social Media Marketing",
            "url": "https://academy.hubspot.com/courses/social-media-marketing",
            "description": "Social media marketing certification"
        },
        {
            "name": "Digital Marketing",
            "url": "https://academy.hubspot.com/courses/digital-marketing",
            "description": "Comprehensive digital marketing course"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for cert in self.CERTIFICATIONS:
            courses.append({
                "platform": "hubspot",
                "name": cert["name"],
                "url": cert["url"],
                "description": cert["description"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
