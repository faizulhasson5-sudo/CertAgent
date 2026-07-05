import os
import sys
import yaml
import argparse
from dotenv import load_dotenv

from src.tracker.database import Database
from src.ai.brain import AIBrain
from src.automation.browser import BrowserManager
from src.automation.enrollment import Enroller
from src.automation.navigation import Navigator
from src.automation.content import ContentProcessor
from src.automation.submission import SubmissionHandler
from src.ai.quiz_solver import QuizSolver
from src.notifications.email_notifier import EmailNotifier
from src.discovery.freecodecamp import FreeCodeCampDiscovery
from src.discovery.kaggle import KaggleDiscovery
from src.discovery.google import GoogleDiscovery
from src.discovery.hubspot import HubSpotDiscovery
from src.discovery.github_skills import GitHubSkillsDiscovery
from src.discovery.microsoft import MicrosoftLearnDiscovery
from src.discovery.google_cloud import GoogleCloudDiscovery
from src.discovery.aws import AWSDiscovery
from src.scheduler.scheduler import AgentScheduler
from src.utils.helpers import random_delay
from src.utils.logger import setup_logger

logger = setup_logger()
load_dotenv()


class CertAgent:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.db = Database(self.config["paths"]["database"])
        self.ai = AIBrain(
            model=self.config["ai"]["model"],
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
        )
        self.notifier = EmailNotifier(
            smtp_server=self.config["notifications"]["email"]["smtp_server"],
            smtp_port=self.config["notifications"]["email"]["smtp_port"]
        )
        self.discoverers = [
            FreeCodeCampDiscovery(self.db),
            KaggleDiscovery(self.db),
            GoogleDiscovery(self.db),
            HubSpotDiscovery(self.db),
            GitHubSkillsDiscovery(self.db),
            MicrosoftLearnDiscovery(self.db),
            GoogleCloudDiscovery(self.db),
            AWSDiscovery(self.db),
        ]

    def _load_config(self, path: str) -> dict:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def discover_courses(self):
        logger.info("Discovering new courses...")
        total_new = 0
        for discoverer in self.discoverers:
            try:
                count = discoverer.discover_new_courses()
                total_new += count
                logger.info(f"  {discoverer.__class__.__name__}: {count} new courses")
            except Exception as e:
                logger.error(f"  Discovery error: {e}")

        logger.info(f"Total new courses discovered: {total_new}")
        self.db.log_activity("discovery", f"Found {total_new} new courses")
        return total_new

    def continue_learning(self):
        logger.info("Continuing learning sessions...")
        courses = self.db.get_courses_by_status("enrolled")
        courses += self.db.get_courses_by_status("in_progress")

        if not courses:
            courses = self.db.get_courses_by_status("discovered")
            if not courses:
                logger.info("No courses to work on. Run discovery first.")
                return

        max_simultaneous = self.config["agent"]["max_courses_simultaneous"]
        courses = courses[:max_simultaneous]

        for course in courses:
            try:
                self._work_on_course(course)
            except Exception as e:
                logger.error(f"Error working on course {course['name']}: {e}")

    def _work_on_course(self, course: dict):
        logger.info(f"Working on: {course['name']} ({course['platform']})")

        if course["platform"] == "github_skills":
            self._work_on_github_skill(course)
        else:
            self._work_on_browser_course(course)

    def _work_on_github_skill(self, course: dict):
        from src.automation.github import GitHubSkillsAutomation

        gh = GitHubSkillsAutomation()
        if not gh.is_authenticated:
            logger.error("GitHub CLI not authenticated")
            return

        self.db.start_course(course["id"])

        result = gh.complete_skill(course["name"])

        if result["success"]:
            logger.info(f"Completed skill: {course['name']}")
            self.db.update_course_progress(course["id"], 100)
            self.db.complete_course(course["id"], result.get("url", ""))
            self.db.log_activity("github_skill_completed",
                f"Completed {course['name']}: {result.get('url', '')}")

            self.notifier.send_notification(
                f"GitHub Skill Completed: {course['name']}",
                f"Repo: {result.get('url', '')}\n\n"
                f"Files created: {', '.join(result.get('files_created', []))}\n\n"
                f"Badge should be awarded soon!"
            )
        else:
            logger.error(f"Failed: {result.get('error', 'Unknown error')}")

    def _work_on_browser_course(self, course: dict):
        with BrowserManager(headless=self.config["agent"]["headless"]) as bm:
            self.db.start_course(course["id"])

            nav = Navigator(bm)
            content = ContentProcessor(bm)
            submission = SubmissionHandler(bm, self.ai)
            quiz_solver = QuizSolver(self.ai, submission, self.notifier,
                                    self.config["agent"]["auto_submit_threshold"] / 100)

            nav.navigate_to_lesson(course["url"])

            lessons = nav.get_course_lessons()
            if lessons:
                self._process_lessons(course, lessons, nav, content, submission, quiz_solver)
            else:
                self._process_current_page(course, nav, content, submission, quiz_solver)

    def _process_lessons(self, course, lessons, nav, content, submission, quiz_solver):
        for lesson in lessons[:5]:
            logger.info(f"  Processing: {lesson['name']}")

            if not nav.navigate_to_lesson(lesson["url"]):
                continue

            self._process_current_page(course, nav, content, submission, quiz_solver)
            random_delay(2, 5)

    def _process_current_page(self, course, nav, content, submission, quiz_solver):
        if nav.is_challenge_page():
            lesson_text = content.read_lesson_content()
            editor_code = content.get_code_editor_content()

            if lesson_text and editor_code is not None:
                ai_solution = quiz_solver.attempt_code_challenge(lesson_text, editor_code)
                if ai_solution:
                    content.set_code_editor_content(ai_solution)
                    random_delay(1, 2)
                    content.click_run_tests()
                    random_delay(2, 3)

                    results = content.get_test_results()
                    if results["passed"]:
                        content.submit_and_continue()
                        logger.info("    Challenge passed!")
                    else:
                        logger.info("    Tests failed, needs human review")
                        self.notifier.send_notification(
                            f"Challenge Failed: {course['name']}",
                            f"Tests output:\n{results['output'][:500]}"
                        )

        elif nav.is_quiz_page():
            questions = nav.get_quiz_questions()
            if questions:
                results = quiz_solver.attempt_quiz(questions, course["name"])
                for r in results:
                    self.db.add_quiz_attempt(
                        course["id"], r["question"],
                        str(r.get("options", [])),
                        r["answer"], r["confidence"]
                    )

    def check_pending_quizzes(self):
        pending = self.db.get_pending_quizzes()
        if pending:
            logger.info(f"Found {len(pending)} pending quizzes")
            for quiz in pending:
                logger.info(f"  Quiz: {quiz['question'][:50]}...")

    def send_progress_report(self):
        stats = self.db.get_stats()
        self.notifier.send_progress_update(stats)
        self.db.log_activity("report", f"Stats: {stats}")

    def download_certificates(self):
        courses = self.db.get_courses_by_status("completed")
        for course in courses:
            if not course.get("certificate_path"):
                logger.info(f"Checking certificate for: {course['name']}")
                with BrowserManager(headless=True) as bm:
                    bm.navigate(course["url"])
                    content = ContentProcessor(bm)
                    cert_path = content.download_certificate(course["name"])
                    if cert_path:
                        self.db.complete_course(course["id"], cert_path)

    def show_status(self):
        stats = self.db.get_stats()
        courses = self.db.get_all_courses()

        print("\n" + "=" * 50)
        print("  CERT AGENT STATUS")
        print("=" * 50)
        print(f"  Total courses: {stats['total']}")
        print(f"  Completed:     {stats['completed']}")
        print(f"  In progress:   {stats['in_progress']}")
        print(f"  Enrolled:      {stats['enrolled']}")
        print(f"  Discovered:    {stats['discovered']}")
        print("=" * 50)

        if courses:
            print("\nCourses:")
            for c in courses[:10]:
                status_icon = {
                    "completed": "[✓]",
                    "in_progress": "[>]",
                    "enrolled": "[E]",
                    "discovered": "[?]"
                }.get(c["status"], "[ ]")
                print(f"  {status_icon} {c['name']} ({c['platform']})")

        print()


def main():
    parser = argparse.ArgumentParser(description="CertAgent - Free Certificate Auto-Learner")
    parser.add_argument("--config", default="config/settings.yaml", help="Config file path")
    parser.add_argument("--discover", action="store_true", help="Discover new courses")
    parser.add_argument("--learn", action="store_true", help="Continue learning")
    parser.add_argument("--run", action="store_true", help="Run full agent cycle")
    parser.add_argument("--schedule", action="store_true", help="Run with scheduler")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--dashboard", action="store_true", help="Open web dashboard")
    parser.add_argument("--test-ai", action="store_true", help="Test AI connection")
    args = parser.parse_args()

    agent = CertAgent(args.config)

    if args.test_ai:
        print("Testing Ollama connection...")
        if agent.ai.test_connection():
            print("Ollama connected successfully!")
        else:
            print("Ollama connection failed. Make sure Ollama is running.")
        return

    if args.discover:
        agent.discover_courses()
    elif args.learn:
        agent.continue_learning()
    elif args.run:
        agent.discover_courses()
        agent.continue_learning()
    elif args.schedule:
        scheduler = AgentScheduler(agent)
        scheduler.schedule_discovery(24)
        scheduler.schedule_learning(2)
        scheduler.schedule_quiz_check(30)
        scheduler.schedule_progress_report(9)
        scheduler.run()
    elif args.status:
        agent.show_status()
    elif args.dashboard:
        from export_data import export_data
        from serve_dashboard import start_server, auto_refresh
        import threading
        import webbrowser

        export_data()
        print("Starting dashboard...")
        refresh_thread = threading.Thread(target=auto_refresh, args=(30,), daemon=True)
        refresh_thread.start()
        webbrowser.open("http://localhost:8080")
        start_server(8080)
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  python main.py --discover      # Find free courses")
        print("  python main.py --learn          # Start learning")
        print("  python main.py --run            # Full cycle")
        print("  python main.py --schedule       # Run continuously")
        print("  python main.py --dashboard      # Open web dashboard")
        print("  python main.py --test-ai        # Test AI connection")


if __name__ == "__main__":
    main()
