import sqlite3
import os
from datetime import datetime
from typing import Optional


class Database:
    def __init__(self, db_path: str = "data/cert_agent.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT DEFAULT 'discovered',
                progress REAL DEFAULT 0.0,
                enrolled_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                certificate_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT,
                status TEXT DEFAULT 'pending',
                order_index INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                lesson_id INTEGER,
                question TEXT NOT NULL,
                options TEXT,
                correct_answer TEXT,
                ai_answer TEXT,
                ai_confidence REAL,
                human_answer TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                sent_at TIMESTAMP,
                responded_at TIMESTAMP,
                response TEXT,
                related_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def add_course(self, platform: str, name: str, url: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO courses (platform, name, url) VALUES (?, ?, ?)",
            (platform, name, url)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_course_status(self, course_id: int, status: str):
        self.conn.execute(
            "UPDATE courses SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, course_id)
        )
        self.conn.commit()

    def update_course_progress(self, course_id: int, progress: float):
        self.conn.execute(
            "UPDATE courses SET progress = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (progress, course_id)
        )
        self.conn.commit()

    def enroll_course(self, course_id: int):
        self.conn.execute(
            "UPDATE courses SET status = 'enrolled', enrolled_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (course_id,)
        )
        self.conn.commit()

    def start_course(self, course_id: int):
        self.conn.execute(
            "UPDATE courses SET status = 'in_progress', started_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (course_id,)
        )
        self.conn.commit()

    def complete_course(self, course_id: int, certificate_path: str):
        self.conn.execute(
            "UPDATE courses SET status = 'completed', completed_at = CURRENT_TIMESTAMP, certificate_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (certificate_path, course_id)
        )
        self.conn.commit()

    def get_courses_by_status(self, status: str) -> list:
        cursor = self.conn.execute(
            "SELECT * FROM courses WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_all_courses(self) -> list:
        cursor = self.conn.execute("SELECT * FROM courses ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_course(self, course_id: int) -> Optional[dict]:
        cursor = self.conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def course_exists(self, platform: str, url: str) -> bool:
        cursor = self.conn.execute(
            "SELECT 1 FROM courses WHERE platform = ? AND url = ?",
            (platform, url)
        )
        return cursor.fetchone() is not None

    def add_quiz_attempt(self, course_id: int, question: str, options: str = None,
                         ai_answer: str = None, ai_confidence: float = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO quiz_attempts (course_id, question, options, ai_answer, ai_confidence) VALUES (?, ?, ?, ?, ?)",
            (course_id, question, options, ai_answer, ai_confidence)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_quiz_human_answer(self, quiz_id: int, human_answer: str):
        self.conn.execute(
            "UPDATE quiz_attempts SET human_answer = ?, status = 'answered' WHERE id = ?",
            (human_answer, quiz_id)
        )
        self.conn.commit()

    def log_activity(self, action: str, details: str = None):
        self.conn.execute(
            "INSERT INTO activity_log (action, details) VALUES (?, ?)",
            (action, details)
        )
        self.conn.commit()

    def get_pending_quizzes(self) -> list:
        cursor = self.conn.execute(
            "SELECT q.*, c.name as course_name FROM quiz_attempts q "
            "JOIN courses c ON q.course_id = c.id "
            "WHERE q.status = 'pending' ORDER BY q.created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        cursor = self.conn.cursor()
        stats = {}
        for status in ['discovered', 'enrolled', 'in_progress', 'completed']:
            cursor.execute("SELECT COUNT(*) FROM courses WHERE status = ?", (status,))
            stats[status] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM courses")
        stats['total'] = cursor.fetchone()[0]
        return stats

    def close(self):
        self.conn.close()
