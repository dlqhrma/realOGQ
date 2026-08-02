import sqlite3

conn = sqlite3.connect("cbt.db")
cursor = conn.cursor()

# 시험 기록
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# 오답노트
# 오답노트
cursor.execute("""
CREATE TABLE IF NOT EXISTS wrong_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    exam_id INTEGER,
    question_id INTEGER,
    chapter TEXT,
    subcategory TEXT,
    concept TEXT,
    difficulty TEXT,
    question TEXT,
    choices TEXT,
    my_answer INTEGER,
    correct_answer INTEGER,
    explanation TEXT,
    wrong_date TEXT,
    exam_count INTEGER
)
""")

# 문제 풀이 기록
cursor.execute("""
CREATE TABLE IF NOT EXISTS question_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    exam_id INTEGER,
    chapter TEXT,
    is_correct INTEGER
)
""")

conn.commit()
conn.close()

print("DB 생성 완료!")

