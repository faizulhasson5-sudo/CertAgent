import os
from ..utils.helpers import random_delay
from ..utils.logger import setup_logger

logger = setup_logger()


class ContentProcessor:
    def __init__(self, browser_manager):
        self.bm = browser_manager
        self.page = browser_manager.page

    def read_lesson_content(self) -> str:
        try:
            selectors = [
                '.challenge-instructions',
                'article',
                '.markdown',
                'main .content'
            ]
            for selector in selectors:
                element = self.page.query_selector(selector)
                if element:
                    return element.inner_text()
            return self.page.inner_text("main")
        except Exception as e:
            logger.error(f"Error reading content: {e}")
            return ""

    def get_code_editor_content(self) -> str:
        try:
            editor = self.page.query_selector('#editor, textarea, .CodeMirror')
            if editor:
                return editor.inner_text()
            return ""
        except Exception as e:
            logger.error(f"Error reading editor: {e}")
            return ""

    def set_code_editor_content(self, code: str):
        try:
            editor = self.page.query_selector('#editor, textarea')
            if editor:
                editor.fill(code)
                return

            self.page.evaluate(f"""() => {{
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{code}`);
                }}
            }}""")
        except Exception as e:
            logger.error(f"Error setting editor content: {e}")

    def click_run_tests(self) -> bool:
        try:
            btn = self.page.query_selector(
                'button:has-text("Run the Tests"), button:has-text("Run"), button:has-text("Test")'
            )
            if btn:
                btn.click()
                random_delay(2, 3)
                return True
            return False
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False

    def get_test_results(self) -> dict:
        try:
            output_el = self.page.query_selector('.test-output, .output, #output, pre')
            output = output_el.inner_text() if output_el else ""

            submit_btn = self.page.query_selector('button:has-text("Submit")')
            passed = "passed" in output.lower() or submit_btn is not None

            return {"passed": passed, "output": output, "has_submit": submit_btn is not None}
        except Exception as e:
            return {"passed": False, "output": str(e), "has_submit": False}

    def submit_and_continue(self) -> bool:
        try:
            submit_btn = self.page.query_selector('button:has-text("Submit and go to next")')
            if submit_btn:
                submit_btn.click()
                random_delay(2, 3)
                return True

            submit_btn = self.page.query_selector('button:has-text("Submit")')
            if submit_btn:
                submit_btn.click()
                random_delay(2, 3)
                return True
            return False
        except Exception as e:
            logger.error(f"Error submitting: {e}")
            return False

    def download_certificate(self, course_name: str) -> str:
        try:
            cert_dir = "data/certificates"
            os.makedirs(cert_dir, exist_ok=True)

            cert_link = self.page.query_selector(
                'a:has-text("Download"), a[href*="certificate"], a:has-text("View")'
            )
            if cert_link:
                cert_url = cert_link.get_attribute("href")
                if cert_url:
                    logger.info(f"Certificate URL found: {cert_url}")
                    return cert_url

            logger.info("No direct certificate download found, checking page...")
            self.bm.screenshot(f"cert_{course_name.replace(' ', '_')}")
            return None

        except Exception as e:
            logger.error(f"Error downloading certificate: {e}")
            return None
