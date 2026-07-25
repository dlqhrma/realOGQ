import sqlite3

DB_NAME = "cbt.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def save_exam(exam_date, score, total_questions, duration):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO exams
        (exam_date, score, total_questions, duration)
        VALUES (?, ?, ?, ?)
    """, (exam_date, score, total_questions, duration))

    exam_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return exam_id
def save_wrong_answer(
    exam_id,
    question_id,
    chapter,
    concept,
    difficulty,
    question,
    choices,
    my_answer,
    correct_answer,
    explanation,
    wrong_date
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wrong_answers (
            exam_id,
            question_id,
            chapter,
            concept,
            difficulty,
            question,
            choices,
            my_answer,
            correct_answer,
            explanation,
            wrong_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
            exam_id,
            question_id,
            chapter,
            concept,
            difficulty,
            question,
            str(choices),
            my_answer,
            correct_answer,
            explanation,
            wrong_date
         ))

    conn.commit()
    conn.close()
def get_exam_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            e.id,
            e.exam_date,
            e.score,
            e.total_questions,
            COUNT(w.id)
        FROM exams e
        LEFT JOIN wrong_answers w
            ON e.id = w.exam_id
        GROUP BY e.id
        ORDER BY e.id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data
def get_wrong_questions(exam_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        chapter,
        concept,
        difficulty,
        question,
        choices,
        my_answer,
        correct_answer,
        explanation
    FROM wrong_answers
    WHERE exam_id = ?
    """, (exam_id,))

    data = cursor.fetchall()

    conn.close()

    return data
