from typing import List, Dict
from .base import BaseDiscovery


class FreeCodeCampDiscovery(BaseDiscovery):
    CERTIFICATIONS = [
        {
            "name": "Responsive Web Design",
            "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
            "description": "Learn HTML and CSS by building 5 responsive web pages"
        },
        {
            "name": "JavaScript Algorithms and Data Structures",
            "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/",
            "description": "Master JavaScript fundamentals and ES6 features"
        },
        {
            "name": "Front End Development Libraries",
            "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/",
            "description": "Learn React, Redux, Bootstrap, jQuery, and Sass"
        },
        {
            "name": "Data Visualization",
            "url": "https://www.freecodecamp.org/learn/data-visualization/",
            "description": "Learn D3.js and data visualization techniques"
        },
        {
            "name": "Apis and Microservices",
            "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
            "description": "Build Node.js APIs and microservices"
        },
        {
            "name": "Quality Assurance",
            "url": "https://www.freecodecamp.org/learn/quality-assurance/",
            "description": "Learn testing with Chai, Jest, and Selenium"
        },
        {
            "name": "Scientific Computing with Python",
            "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
            "description": "Build Python programs and learn OOP"
        },
        {
            "name": "Data Analysis with Python",
            "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
            "description": "Learn data analysis with NumPy, Pandas, and Matplotlib"
        },
        {
            "name": "Machine Learning with Python",
            "url": "https://www.freecodecamp.org/learn/machine-learning-with-python/",
            "description": "Build ML models with TensorFlow and scikit-learn"
        },
        {
            "name": "Relational Database",
            "url": "https://www.freecodecamp.org/learn/relational-database/",
            "description": "Learn SQL, Bash, and PostgreSQL"
        },
        {
            "name": "Coding Interview Prep",
            "url": "https://www.freecodecamp.org/learn/coding-interview-prep/",
            "description": "Algorithms and data structures for interviews"
        },
    ]

    def discover_courses(self) -> List[Dict]:
        courses = []
        for cert in self.CERTIFICATIONS:
            courses.append({
                "platform": "freecodecamp",
                "name": cert["name"],
                "url": cert["url"],
                "description": cert["description"]
            })
        return courses

    def discover_new_courses(self) -> int:
        courses = self.discover_courses()
        return self.save_new_courses(courses)
