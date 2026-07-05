from ..utils.helpers import random_delay
from ..utils.logger import setup_logger

logger = setup_logger()


class Navigator:
    def __init__(self, browser_manager):
        self.bm = browser_manager
        self.page = browser_manager.page

    def get_course_lessons(self) -> list:
        lessons = []

        try:
            lesson_links = self.page.query_selector_all('a[href*="/learn/"], li a, .challenge a, .block a')
            for link in lesson_links:
                href = link.get_attribute("href")
                text = link.inner_text().strip()
                if href and text and len(text) > 2:
                    lessons.append({"name": text, "url": href})
        except Exception as e:
            logger.error(f"Error getting lessons: {e}")

        return lessons

    def navigate_to_lesson(self, lesson_url: str) -> bool:
        try:
            if not lesson_url.startswith("http"):
                base = "https://www.freecodecamp.org"
                lesson_url = base + lesson_url

            self.page.goto(lesson_url, wait_until="domcontentloaded")
            random_delay(2, 3)
            return True
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False

    def get_page_content(self) -> str:
        try:
            content_area = self.page.query_selector('.challenge-instructions, article, main')
            if content_area:
                return content_area.inner_text()
            return self.page.inner_text("main")
        except Exception as e:
            logger.error(f"Error getting content: {e}")
            return ""

    def is_challenge_page(self) -> bool:
        return bool(self.page.query_selector(
            '.challenge-instructions, textarea, #editor, [data-type="stdin"], code-block'
        ))

    def is_quiz_page(self) -> bool:
        return bool(self.page.query_selector(
            'quiz, .quiz, [class*="quiz"], form, input[type="radio"], input[type="checkbox"]'
        ))

    def get_quiz_questions(self) -> list:
        questions = []
        try:
            question_elements = self.page.query_selector_all('.quiz-question, .question, [class*="question"]')
            for i, q_el in enumerate(question_elements):
                question_text = q_el.inner_text()
                options = []
                option_elements = self.page.query_selector_all(
                    f'.quiz-question:nth-child({i+1}) option, .question:nth-child({i+1}) label'
                )
                for opt in option_elements:
                    options.append(opt.inner_text())
                questions.append({
                    "question": question_text,
                    "options": options,
                    "index": i
                })
        except Exception as e:
            logger.error(f"Error getting quiz questions: {e}")

        return questions

    def click_next(self) -> bool:
        try:
            next_btn = self.page.query_selector(
                'button:has-text("Next"), a:has-text("Next"), button[type="submit"]'
            )
            if next_btn:
                next_btn.click()
                random_delay(2, 3)
                return True
            return False
        except Exception as e:
            logger.error(f"Error clicking next: {e}")
            return False

    def submit_answer(self, answer: str) -> bool:
        try:
            textarea = self.page.query_selector('textarea, #editor, [data-type="stdin"]')
            if textarea:
                textarea.fill(answer)
                random_delay(0.5, 1)

            submit_btn = self.page.query_selector(
                'button:has-text("Run"), button:has-text("Submit"), button[type="submit"]'
            )
            if submit_btn:
                submit_btn.click()
                random_delay(2, 3)
                return True
            return False
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return False

    def check_test_results(self) -> dict:
        try:
            output = self.page.inner_text('.output, .test-output, pre, code')
            passed = "passed" in output.lower() or "tests: passed" in output.lower()
            return {"passed": passed, "output": output}
        except Exception as e:
            return {"passed": False, "output": str(e)}
