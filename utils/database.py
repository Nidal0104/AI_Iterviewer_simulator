import sqlite3
from datetime import datetime

DB_NAME = "interview.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_role TEXT,
        date TEXT,
        overall_score REAL,
        result TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS questions_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER,
        question TEXT,
        user_answer TEXT,
        technical_score REAL,
        grammar_score REAL,
        clarity_score REAL,
        confidence_score REAL,
        overall_score REAL,
        improved_answer TEXT,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_interview(job_role, overall_score, result):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO interviews (job_role, date, overall_score, result)
        VALUES (?, ?, ?, ?)
    """, (job_role, date, overall_score, result))

    interview_id = c.lastrowid
    conn.commit()
    conn.close()

    return interview_id


def save_question_answer(interview_id, data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO questions_answers
        (interview_id, question, user_answer, technical_score,
        grammar_score, clarity_score, confidence_score,
        overall_score, improved_answer, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        interview_id,
        data["question"],
        data["user_answer"],
        data["technical_score"],
        data["grammar_score"],
        data["clarity_score"],
        data["confidence_score"],
        data["overall_score"],
        data["improved_answer"],
        data["feedback"]
    ))

    conn.commit()
    conn.close()


def get_interview_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM interviews ORDER BY date DESC")
    rows = c.fetchall()

    conn.close()
    return rows
