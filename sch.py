"""Student Marks Database Manager
A command-line Python application to manage student records using SQLite.

Fix: `school.db` may already contain a `students` table with a different schema
(e.g., columns: id, name, age, email, class_no). This script will detect that
mismatch and recreate the table so the app works consistently.
"""

import sqlite3


# ─────────────────────────────────────────────
# (a) Database & Table Setup
# ─────────────────────────────────────────────

def create_connection(db_file="school.db"):
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # allows column-name access
    return conn


def create_table(conn):
    """Create (or fix) the `students` table schema."""

    # Check if table exists
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='students';"
    ).fetchone()

    required = {"id", "name", "subject", "marks", "grade"}

    if table_exists:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(students);").fetchall()}
        if not required.issubset(cols):
            # Schema mismatch -> drop & recreate
            conn.execute("DROP TABLE IF EXISTS students;")

    sql = """
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            subject TEXT,
            marks   INTEGER,
            grade   TEXT
        );
    """
    conn.execute(sql)
    conn.commit()
    print("✔  Table 'students' is ready.\n")


# ─────────────────────────────────────────────
# (b) Insert Student with Auto Grade
# ─────────────────────────────────────────────

def compute_grade(marks: int) -> str:
    """Return the letter grade for a given marks value."""
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    else:
        return "F"


def insert_student(conn, name, subject, marks):
    """Insert a student record with computed grade."""
    grade = compute_grade(marks)
    sql = "INSERT INTO students (name, subject, marks, grade) VALUES (?, ?, ?, ?);"
    cur = conn.execute(sql, (name, subject, marks, grade))
    conn.commit()
    print(
        f"  ➕  Inserted: {name} | {subject} | Marks: {marks} | Grade: {grade}  (id={cur.lastrowid})"
    )
    return cur.lastrowid


# ─────────────────────────────────────────────
# (c) Top-N Students by Marks
# ─────────────────────────────────────────────

def get_top_students(conn, n):
    """Return top-n students sorted by marks descending."""
    sql = """
        SELECT id, name, subject, marks, grade
        FROM   students
        ORDER  BY marks DESC
        LIMIT  ?;
    """
    return conn.execute(sql, (n,)).fetchall()


# ─────────────────────────────────────────────
# (d) Average Marks per Subject
# ─────────────────────────────────────────────

def subject_average(conn):
    """Return average marks grouped by subject."""
    sql = """
        SELECT   subject,
                 ROUND(AVG(marks), 2) AS avg_marks
        FROM     students
        GROUP BY subject
        ORDER BY avg_marks DESC;
    """
    return conn.execute(sql).fetchall()


# ─────────────────────────────────────────────
# (e) Delete Failed Students
# ─────────────────────────────────────────────

def delete_failed_students(conn):
    """Delete every student whose grade is 'F'."""
    sql = "DELETE FROM students WHERE grade = 'F';"
    cur = conn.execute(sql)
    conn.commit()
    count = cur.rowcount
    print(f"  🗑   Deleted {count} failed student(s) with grade 'F'.")
    return count


# ─────────────────────────────────────────────
# Display Helpers
# ─────────────────────────────────────────────

def print_students(rows, title="Students"):
    """Pretty-print a list of student rows."""
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")
    if not rows:
        print("  (no records found)")
    else:
        print(f"  {'ID':<4} {'Name':<18} {'Subject':<12} {'Marks':<7} {'Grade'}")
        print(f"  {'─'*4} {'─'*18} {'─'*12} {'─'*7} {'─'*5}")
        for r in rows:
            print(
                f"  {r['id']:<4} {r['name']:<18} {r['subject']:<12} {r['marks']:<7} {r['grade']}"
            )
    print(f"{'─'*55}\n")


def print_averages(rows):
    """Pretty-print subject averages."""
    print(f"\n{'─'*35}")
    print("  Subject Averages")
    print(f"{'─'*35}")
    if not rows:
        print("  (no data)")
    else:
        print(f"  {'Subject':<18} {'Avg Marks'}")
        print(f"  {'─'*18} {'─'*9}")
        for r in rows:
            print(f"  {r['subject']:<18} {r['avg_marks']}")
    print(f"{'─'*35}\n")


# ─────────────────────────────────────────────
# (f) Main
# ─────────────────────────────────────────────

def main():
    conn = None
    try:
        conn = create_connection("school.db")
        create_table(conn)

        print("Inserting sample students …")
        sample_data = [
            ("Alice", "Math", 95),
            ("Bob", "Science", 82),
            ("Charlie", "Math", 73),
            ("Diana", "English", 67),
            ("Eve", "Science", 55),
            ("Frank", "English", 91),
            ("Grace", "Math", 48),
            ("Henry", "Science", 88),
            ("Ivy", "English", 76),
            ("Jack", "Math", 60),
        ]

        for name, subject, marks in sample_data:
            insert_student(conn, name, subject, marks)

        top5 = get_top_students(conn, 5)
        print_students(top5, title="Top 5 Students by Marks")

        avgs = subject_average(conn)
        print_averages(avgs)

        print("Removing students who failed (grade = 'F') …")
        delete_failed_students(conn)

        all_students = conn.execute(
            "SELECT * FROM students ORDER BY marks DESC;"
        ).fetchall()
        print_students(all_students, title="All Students After Deletion")

    except sqlite3.DatabaseError as db_err:
        print(f"\n❌  Database error: {db_err}")

    except Exception as err:
        print(f"\n❌  Unexpected error: {err}")

    finally:
        if conn:
            conn.close()
            print("✔  Database connection closed.")


if __name__ == "__main__":
    main()

