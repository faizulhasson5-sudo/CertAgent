import schedule
import time
from datetime import datetime
from ..utils.logger import setup_logger

logger = setup_logger()


class AgentScheduler:
    def __init__(self, agent):
        self.agent = agent
        self.jobs = []

    def schedule_discovery(self, interval_hours: int = 24):
        job = schedule.every(interval_hours).hours.do(self.agent.discover_courses)
        self.jobs.append(job)
        logger.info(f"Scheduled course discovery every {interval_hours} hours")

    def schedule_learning(self, interval_hours: int = 1):
        job = schedule.every(interval_hours).hours.do(self.agent.continue_learning)
        self.jobs.append(job)
        logger.info(f"Scheduled learning session every {interval_hours} hours")

    def schedule_progress_report(self, hour: int = 9):
        job = schedule.every().day.at(f"{hour:02d}:00").do(self.agent.send_progress_report)
        self.jobs.append(job)
        logger.info(f"Scheduled daily progress report at {hour:02d}:00")

    def schedule_quiz_check(self, interval_minutes: int = 30):
        job = schedule.every(interval_minutes).minutes.do(self.agent.check_pending_quizzes)
        self.jobs.append(job)
        logger.info(f"Scheduled quiz check every {interval_minutes} minutes")

    def run(self):
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        self.agent.discover_courses()
        self.agent.continue_learning()

        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_once(self):
        logger.info("Running one-time agent cycle...")
        self.agent.discover_courses()
        self.agent.continue_learning()
        self.agent.check_pending_quizzes()
        logger.info("Agent cycle complete")
