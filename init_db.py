import sqlite3

conn = sqlite3.connect("cbt.db")
cursor = conn.cursor()

# 시험 기록
cursor.execute("""
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_date TEXT,
    score INTEGER,
    total_questions INTEGER,
    duration INTEGER
)
""")

# 오답노트
# 오답노트
cursor.execute("""
CREATE TABLE IF NOT EXISTS wrong_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    question_id INTEGER,
    chapter TEXT,
    concept TEXT,
    difficulty TEXT,
    question TEXT,
    choices TEXT,
    my_answer INTEGER,
    correct_answer INTEGER,
    explanation TEXT,
    wrong_date TEXT
)
""")

conn.commit()
conn.close()

print("DB 생성 완료!")
