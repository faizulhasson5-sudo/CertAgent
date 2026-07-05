import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tracker.database import Database


def export_data():
    db = Database()

    courses = db.get_all_courses()
    stats = db.get_stats()
    pending_quizzes = db.get_pending_quizzes()

    cursor = db.conn.execute(
        "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 50"
    )
    activity_log = [dict(row) for row in cursor.fetchall()]

    cursor = db.conn.execute(
        "SELECT * FROM quiz_attempts ORDER BY created_at DESC LIMIT 50"
    )
    quiz_attempts = [dict(row) for row in cursor.fetchall()]

    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
        "courses": courses,
        "activity_log": activity_log,
        "quiz_attempts": quiz_attempts,
        "pending_quizzes": pending_quizzes,
    }

    os.makedirs("web", exist_ok=True)
    with open("web/data.json", "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"Data exported to web/data.json")
    print(f"Stats: {stats}")
    db.close()


if __name__ == "__main__":
    export_data()
