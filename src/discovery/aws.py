from typing import List, Dict
from .base import BaseDiscovery


class AWSDiscovery(BaseDiscovery):
    COURSES = [
        {
            "name": "AWS Cloud Practitioner Essentials",
            "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
            "description": "AWS cloud fundamentals",
            "badge": "aws-practitioner"
        },
        {
            "name": "AWS Technical Essentials",
            "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/48/aws-technical-essentials",
            "description": "Core AWS services",
            "badge": "aws-technical"
        },
        {
            "name": "Introduction to Security on AWS",
            "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/199/introduction-to-security-on-aws",
            "description": "AWS security basics",
            "badge": "aws-security"
        },
        {
            "name": "Introduction to Machine Learning on AWS",
            "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/200/introduction-to-machine-learning-on-aws",
            "description": "ML services on AWS",
            "badge": "aws-ml"
        },
        {
            "name": "AWS Cloud Economics",
            "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/1894/aws-cloud-economics",
            "description": "Cloud cost optimization",
            "badge": "aws-economics"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for course in self.COURSES:
            courses.append({
                "platform": "aws",
                "name": course["name"],
                "url": course["url"],
                "description": course["description"],
                "badge": course["badge"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
