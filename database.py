import sqlite3

DB_NAME = "cbt.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def save_exam(user_id, exam_date, score, total_questions, duration):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO exams
        (user_id, exam_date, score, total_questions, duration)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, exam_date, score, total_questions, duration))

    exam_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return exam_id
def save_wrong_answer(
    user_id,
    exam_id,
    question_id,
    chapter,
    subcategory,
    concept,
    difficulty,
    question,
    choices,
    my_answer,
    correct_answer,
    explanation,
    wrong_date,
    exam_count
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wrong_answers (
            user_id,
            exam_id,
            question_id,
            chapter,
            subcategory,
            concept,
            difficulty,
            question,
            choices,
            my_answer,
            correct_answer,
            explanation,
            wrong_date,
            exam_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
            user_id,
            exam_id,
            question_id,
            chapter,
            subcategory,
            concept,
            difficulty,
            question,
            str(choices),
            my_answer,
            correct_answer,
            explanation,
            wrong_date,
            exam_count
        ))

    conn.commit()
    conn.close()
def get_exam_history_for_note(user_id):
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
        WHERE e.user_id = ?
        GROUP BY e.id
        ORDER BY e.id DESC
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    return data
def get_wrong_questions(user_id, exam_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        chapter,
        subcategory,
        concept,
        difficulty,
        question,
        choices,
        my_answer,
        correct_answer,
        explanation
        FROM wrong_answers
        WHERE user_id = ?
        AND exam_id = ?
    """, (user_id, exam_id))

    data = cursor.fetchall()

    conn.close()

    return data
def get_exam_history(user_id):
    conn = sqlite3.connect("cbt.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            exam_date,
            score,
            total_questions,
            duration
        FROM exams
        WHERE user_id = ?
        ORDER BY id ASC
    """,(user_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_chapter_statistics(user_id):
    conn = sqlite3.connect("cbt.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            chapter,
            COUNT(*) AS wrong_count
        FROM wrong_answers
        WHERE user_id = ?
        GROUP BY chapter
    """,(user_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows

def save_question_history(
    user_id,
    exam_id,
    chapter,
    is_correct
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO question_history(
            user_id,
            exam_id,
            chapter,
            is_correct
        )
        VALUES (?, ?, ?, ?)
    """, (
            user_id,
            exam_id,
            chapter,
            is_correct
        ))

    conn.commit()
    conn.close()
    
def get_chapter_accuracy(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            chapter,
            ROUND(AVG(is_correct) * 100, 1)
        FROM question_history
        WHERE user_id = ?
        GROUP BY chapter
    """, (user_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users(username, password)
            VALUES (?, ?)
        """, (username, password))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE username = ?
        AND password = ?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    return user