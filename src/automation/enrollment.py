import os
from ..utils.helpers import random_delay
from ..utils.logger import setup_logger

logger = setup_logger()


class Enroller:
    def __init__(self, browser_manager):
        self.bm = browser_manager
        self.page = browser_manager.page

    def login_freecodecamp(self, username: str, password: str) -> bool:
        try:
            self.page.goto("https://www.freecodecamp.org/sign-in", wait_until="domcontentloaded")
            random_delay(2, 3)

            self.page.fill('input[id="campui-email-address"]', username)
            random_delay(0.5, 1)
            self.page.fill('input[id="campui-password"]', password)
            random_delay(0.5, 1)

            self.page.click('button[type="submit"]')
            self.page.wait_for_load_state("networkidle")
            random_delay(2, 3)

            if "learn" in self.page.url or "settings" in self.page.url:
                logger.info("Successfully logged into freeCodeCamp")
                self.bm.save_state()
                return True
            else:
                logger.warning("Login may have failed, checking...")
                self.bm.screenshot("login_result")
                return False

        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.bm.screenshot("login_error")
            return False

    def login_kaggle(self, username: str, password: str) -> bool:
        try:
            self.page.goto("https://www.kaggle.com/account/login", wait_until="domcontentloaded")
            random_delay(2, 3)

            self.page.fill('input[name="username"]', username)
            random_delay(0.5, 1)
            self.page.fill('input[name="password"]', password)
            random_delay(0.5, 1)

            self.page.click('button[type="submit"]')
            self.page.wait_for_load_state("networkidle")
            random_delay(2, 3)

            logger.info("Attempting Kaggle login...")
            self.bm.screenshot("kaggle_login_result")
            return True

        except Exception as e:
            logger.error(f"Kaggle login failed: {e}")
            self.bm.screenshot("kaggle_login_error")
            return False

    def enroll_in_course(self, course_url: str, platform: str) -> bool:
        try:
            self.page.goto(course_url, wait_until="domcontentloaded")
            random_delay(2, 3)

            if platform == "freecodecamp":
                return self._enroll_freecodecamp()
            elif platform == "kaggle":
                return self._enroll_kaggle()
            else:
                logger.info(f"No specific enrollment logic for {platform}, course page loaded")
                return True

        except Exception as e:
            logger.error(f"Enrollment failed: {e}")
            self.bm.screenshot("enrollment_error")
            return False

    def _enroll_freecodecamp(self) -> bool:
        try:
            start_btn = self.page.query_selector('a[href*="start"], button:has-text("Start"), a:has-text("Start")')
            if start_btn:
                start_btn.click()
                self.page.wait_for_load_state("networkidle")
                random_delay(2, 3)
                logger.info("Started freeCodeCamp course")
                return True

            logger.info("Course page loaded (no explicit enrollment needed)")
            return True

        except Exception as e:
            logger.error(f"freeCodeCamp enrollment error: {e}")
            return False

    def _enroll_kaggle(self) -> bool:
        try:
            start_btn = self.page.query_selector('button:has-text("Start"), a:has-text("Start Course")')
            if start_btn:
                start_btn.click()
                self.page.wait_for_load_state("networkidle")
                random_delay(2, 3)
                logger.info("Started Kaggle course")
                return True

            logger.info("Kaggle course page loaded")
            return True

        except Exception as e:
            logger.error(f"Kaggle enrollment error: {e}")
            return False
