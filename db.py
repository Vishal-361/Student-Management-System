"""Database helpers using Python's built-in sqlite3 module (no ORM).

One connection is opened per request and stored on Flask's `g` object,
then closed automatically by the teardown handler registered in app.py.
"""

import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no  TEXT    NOT NULL UNIQUE,
    name     TEXT    NOT NULL,
    email    TEXT    NOT NULL,
    phone    TEXT    NOT NULL,
    course   TEXT    NOT NULL,
    semester INTEGER NOT NULL,
    marks    REAL    NOT NULL
);
"""

# Sample records inserted on first run so the app demos instantly.
SAMPLE_STUDENTS = [
    ("CSE-101", "Aarav Sharma", "aarav.sharma@example.com", "9876543210", "B.Tech CSE", 5, 88.5),
    ("CSE-102", "Priya Patel", "priya.patel@example.com", "9876501234", "B.Tech CSE", 5, 92.0),
    ("ECE-201", "Rohan Verma", "rohan.verma@example.com", "9812345678", "B.Tech ECE", 3, 76.5),
    ("BCA-301", "Sneha Reddy", "sneha.reddy@example.com", "9004567890", "BCA", 2, 81.0),
    ("MCA-401", "Vikram Singh", "vikram.singh@example.com", "9988776655", "MCA", 1, 69.5),
    ("CSE-103", "Ananya Gupta", "ananya.gupta@example.com", "9765432109", "B.Tech CSE", 7, 95.0),
    ("ME-501", "Karan Mehta", "karan.mehta@example.com", "9654321098", "B.Tech ME", 4, 73.0),
    ("BSC-601", "Divya Nair", "divya.nair@example.com", "9543210987", "B.Sc Computer Science", 6, 85.5),
]


def get_db():
    """Return the current request's database connection (create if needed)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # Rows behave like dicts, so templates can use student["name"] style access.
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    """Close the connection at the end of the request (teardown handler)."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    """Create the students table and seed sample data if it is empty."""
    conn = get_db()
    conn.execute(SCHEMA)
    count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO students (roll_no, name, email, phone, course, semester, marks)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            SAMPLE_STUDENTS,
        )
    conn.commit()
