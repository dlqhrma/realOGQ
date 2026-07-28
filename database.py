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
def get_exam_history_for_note():
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
def get_exam_history():
    conn = sqlite3.connect("cbt.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            exam_date,
            score,
            total_questions,
            duration
        FROM exams
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_chapter_statistics():
    conn = sqlite3.connect("cbt.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            chapter,
            COUNT(*) AS wrong_count
        FROM wrong_answers
        GROUP BY chapter
        ORDER BY wrong_count DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def save_question_history(
    exam_id,
    chapter,
    is_correct
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO question_history
        (
            exam_id,
            chapter,
            is_correct
        )
        VALUES (?, ?, ?)
    """, (
        exam_id,
        chapter,
        is_correct
    ))

    conn.commit()
    conn.close()
    
def get_chapter_accuracy():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            chapter,
            ROUND(AVG(is_correct) * 100, 1)
        FROM question_history
        GROUP BY chapter
        ORDER BY AVG(is_correct) DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows