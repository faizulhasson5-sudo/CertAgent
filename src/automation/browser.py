import os
import random
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from ..utils.helpers import random_delay


class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=self._random_user_agent(),
            storage_state="data/browser_state.json" if os.path.exists("data/browser_state.json") else None
        )
        self.page = self.context.new_page()
        self._stealth_mode()
        return self.page

    def _random_user_agent(self) -> str:
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        return random.choice(agents)

    def _stealth_mode(self):
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

    def save_state(self):
        self.context.storage_state(path="data/browser_state.json")

    def screenshot(self, name: str = "screenshot"):
        os.makedirs("data/screenshots", exist_ok=True)
        path = f"data/screenshots/{name}.png"
        self.page.screenshot(path=path)
        return path

    def navigate(self, url: str, wait_until: str = "domcontentloaded"):
        self.page.goto(url, wait_until=wait_until)
        random_delay(1, 2)

    def close(self):
        try:
            self.save_state()
        except Exception:
            pass
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()
