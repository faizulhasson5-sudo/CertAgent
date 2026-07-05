from ..utils.helpers import random_delay
from ..utils.logger import setup_logger

logger = setup_logger()


class SubmissionHandler:
    def __init__(self, browser_manager, ai_brain):
        self.bm = browser_manager
        self.page = browser_manager.page
        self.ai = ai_brain

    def handle_code_challenge(self, lesson_content: str, editor_content: str) -> dict:
        challenge_text = f"Challenge:\n{lesson_content}\n\nCurrent code:\n{editor_content}"

        result = self.ai.solve_code_challenge(challenge_text)
        logger.info(f"AI solution confidence: {result['confidence']:.1%}")

        return result

    def handle_quiz(self, questions: list, course_context: str = None) -> list:
        results = []
        for q in questions:
            if q.get("options"):
                result = self.ai.solve_quiz(
                    q["question"],
                    q["options"],
                    context=course_context
                )
            else:
                result = self.ai.solve_code_challenge(q["question"])
                result = {
                    "answer": result.get("code", ""),
                    "explanation": result.get("explanation", ""),
                    "confidence": result.get("confidence", 0.0)
                }

            results.append({**q, **result})
            logger.info(f"Quiz Q: {q['question'][:50]}... -> {result['answer']} ({result['confidence']:.1%})")

        return results

    def should_ask_human(self, confidence: float, threshold: float = 0.85) -> bool:
        return confidence < threshold

    def format_human_request(self, question_data: dict) -> dict:
        subject = f"Help needed: {question_data.get('course_name', 'Unknown Course')}"
        body_parts = [
            f"Question: {question_data.get('question', 'N/A')}",
            ""
        ]

        if question_data.get("options"):
            body_parts.append("Options:")
            for i, opt in enumerate(question_data["options"]):
                letter = chr(65 + i)
                body_parts.append(f"  {letter}) {opt}")
            body_parts.append("")

        body_parts.append(f"AI's best guess: {question_data.get('answer', 'N/A')} "
                         f"({question_data.get('confidence', 0):.0%} confident)")
        body_parts.append(f"Explanation: {question_data.get('explanation', 'N/A')}")
        body_parts.append("")
        body_parts.append("Reply with just the letter (A/B/C/D) or the answer.")

        return {
            "subject": subject,
            "body": "\n".join(body_parts)
        }
