from abc import ABC, abstractmethod
from typing import List, Dict


class BaseDiscovery(ABC):
    def __init__(self, db):
        self.db = db

    @abstractmethod
    def discover_courses(self) -> List[Dict]:
        pass

    def filter_new_courses(self, courses: List[Dict]) -> List[Dict]:
        new_courses = []
        for course in courses:
            if not self.db.course_exists(course["platform"], course["url"]):
                new_courses.append(course)
        return new_courses

    def save_new_courses(self, courses: List[Dict]) -> int:
        new_courses = self.filter_new_courses(courses)
        count = 0
        for course in new_courses:
            self.db.add_course(course["platform"], course["name"], course["url"])
            count += 1
        return count
