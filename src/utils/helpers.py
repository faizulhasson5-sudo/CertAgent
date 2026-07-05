import random
import time


def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def human_like_type_delay():
    time.sleep(random.uniform(0.05, 0.15))


def parse_confidence(confidence_str: str) -> float:
    try:
        val = float(confidence_str)
        return max(0.0, min(1.0, val))
    except (ValueError, TypeError):
        return 0.0


def clean_text(text: str) -> str:
    return " ".join(text.split()).strip()
