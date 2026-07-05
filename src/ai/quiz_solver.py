from ..ai.brain import AIBrain
from ..automation.submission import SubmissionHandler
from ..notifications.email_notifier import EmailNotifier
from ..utils.logger import setup_logger

logger = setup_logger()


class QuizSolver:
    def __init__(self, ai_brain: AIBrain, submission: SubmissionHandler,
                 notifier: EmailNotifier, auto_submit_threshold: float = 0.85):
        self.ai = ai_brain
        self.submission = submission
        self.notifier = notifier
        self.threshold = auto_submit_threshold

    def attempt_quiz(self, questions: list, course_name: str,
                     course_context: str = None) -> list:
        results = self.submission.handle_quiz(questions, course_context)

        for result in results:
            if self.submission.should_ask_human(result["confidence"], self.threshold):
                logger.info(f"Low confidence ({result['confidence']:.0%}), asking human...")
                result["human_answer"] = self._request_human_help(result, course_name)
            else:
                logger.info(f"High confidence ({result['confidence']:.0%}), auto-submitting")
                result["human_answer"] = result["answer"]

        return results

    def _request_human_help(self, question_data: dict, course_name: str) -> str:
        question_data["course_name"] = course_name
        request = self.submission.format_human_request(question_data)

        request_id = f"quiz_{hash(question_data['question']) % 10000}"
        self.notifier.send_notification(
            request["subject"],
            request["body"],
            request_id=request_id
        )

        logger.info("Waiting for human reply via email...")
        reply = self.notifier.wait_for_reply(request_id, timeout_minutes=60)

        if reply:
            logger.info(f"Human answer received: {reply}")
            return reply
        else:
            logger.warning("No human reply, using AI answer")
            return question_data["answer"]

    def attempt_code_challenge(self, challenge_content: str, current_code: str) -> str:
        result = self.submission.handle_code_challenge(challenge_content, current_code)

        if result["confidence"] >= self.threshold:
            logger.info(f"Code solution confidence: {result['confidence']:.0%}, using AI solution")
            return result["code"]
        else:
            logger.info(f"Low confidence code solution: {result['confidence']:.0%}")
            subject = "Code Challenge Help Needed"
            body = (f"Challenge:\n{challenge_content[:500]}\n\n"
                   f"AI Solution ({result['confidence']:.0%} confident):\n{result['code'][:500]}\n\n"
                   f"Reply with your solution code.")
            self.notifier.send_notification(subject, body)
            return None
