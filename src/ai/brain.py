import ollama
import json
from typing import Optional


class AIBrain:
    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.client = ollama.Client(host=host)

    def chat(self, prompt: str, system: str = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": 0.3}
        )
        return response["message"]["content"]

    def solve_quiz(self, question: str, options: list[str], context: str = None) -> dict:
        system_prompt = """You are an expert quiz solver. Analyze the question carefully and provide the best answer.
Always respond in JSON format:
{
    "answer": "the letter of the correct answer (A/B/C/D)",
    "explanation": "brief explanation of why this is correct",
    "confidence": 0.0-1.0
}
Only output the JSON, no other text."""

        options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
        user_prompt = f"Question: {question}\n\nOptions:\n{options_text}"
        if context:
            user_prompt = f"Context: {context}\n\n{user_prompt}"

        response = self.chat(user_prompt, system=system_prompt)

        try:
            result = json.loads(response.strip())
            return {
                "answer": result.get("answer", "A"),
                "explanation": result.get("explanation", ""),
                "confidence": float(result.get("confidence", 0.5))
            }
        except (json.JSONDecodeError, ValueError):
            return {
                "answer": "A",
                "explanation": "Failed to parse AI response",
                "confidence": 0.0
            }

    def solve_code_challenge(self, challenge_description: str, language: str = "python") -> dict:
        system_prompt = f"""You are an expert {language} programmer. Solve the coding challenge.
Always respond in JSON format:
{{
    "code": "the complete solution code",
    "explanation": "brief explanation of the approach",
    "confidence": 0.0-1.0
}}
Only output the JSON, no other text."""

        response = self.chat(challenge_description, system=system_prompt)

        try:
            result = json.loads(response.strip())
            return {
                "code": result.get("code", ""),
                "explanation": result.get("explanation", ""),
                "confidence": float(result.get("confidence", 0.5))
            }
        except (json.JSONDecodeError, ValueError):
            return {
                "code": "",
                "explanation": "Failed to parse AI response",
                "confidence": 0.0
            }

    def summarize_content(self, content: str) -> str:
        system_prompt = "Summarize the following educational content concisely. Focus on key concepts and actionable knowledge."
        return self.chat(content[:4000], system=system_prompt)

    def explain_concept(self, concept: str) -> str:
        system_prompt = "Explain the following concept clearly and concisely, suitable for a student learning it for the first time."
        return self.chat(concept, system=system_prompt)

    def test_connection(self) -> bool:
        try:
            response = self.chat("Say 'connected' in one word.")
            return "connected" in response.lower()
        except Exception as e:
            print(f"Ollama connection failed: {e}")
            return False
