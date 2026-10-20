"""Student routes (Flask Blueprint): list, detail, add, edit, delete.

Keeping every student page in this one blueprint is what makes the
routing "modular" - app.py only registers the blueprint, it does not
know about individual pages.
"""

import re

from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import get_db

students_bp = Blueprint("students", __name__, url_prefix="/students")

# Courses offered - used both for the form dropdown and for validation.
COURSES = [
    "B.Tech CSE",
    "B.Tech ECE",
    "B.Tech ME",
    "BCA",
    "MCA",
    "B.Sc Computer Science",
]

# Simple, readable email pattern: something @ something . something
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

INSERT_SQL = (
    "INSERT INTO students (roll_no, name, email, phone, course, semester, marks)"
    " VALUES (?, ?, ?, ?, ?, ?, ?)"
)


def validate_student(form, current_id=None):
    """Validate submitted form data on the server side.

    Returns (data, errors): `data` holds the cleaned values, `errors`
    is a list of human-readable problems (empty when input is valid).
    `current_id` is the id of the student being edited, so the
    roll-number uniqueness check can ignore that student's own record.
    """
    errors = []
    data = {
        "roll_no": form.get("roll_no", "").strip(),
        "name": form.get("name", "").strip(),
        "email": form.get("email", "").strip(),
        "phone": form.get("phone", "").strip(),
        "course": form.get("course", "").strip(),
    }

    # --- Required text fields -------------------------------------------
    if not data["roll_no"]:
        errors.append("Roll number is required.")
    if not data["name"]:
        errors.append("Name is required.")

    # --- Email format ----------------------------------------------------
    if not EMAIL_RE.match(data["email"]):
        errors.append("A valid email address is required.")

    # --- Phone: digits only, 10 to 15 characters -------------------------
    if not data["phone"].isdigit() or not 10 <= len(data["phone"]) <= 15:
        errors.append("Phone number must be 10 to 15 digits.")

    # --- Course must be one of the known options -------------------------
    if data["course"] not in COURSES:
        errors.append("Please choose a valid course.")

    # --- Semester: whole number between 1 and 8 --------------------------
    try:
        data["semester"] = int(form.get("semester", ""))
        if not 1 <= data["semester"] <= 8:
            errors.append("Semester must be between 1 and 8.")
    except ValueError:
        errors.append("Semester must be a whole number between 1 and 8.")

    # --- Marks: number between 0 and 100 ---------------------------------
    try:
        data["marks"] = float(form.get("marks", ""))
        if not 0 <= data["marks"] <= 100:
            errors.append("Marks must be between 0 and 100.")
    except ValueError:
        errors.append("Marks must be a number between 0 and 100.")

    # --- Roll number must be unique --------------------------------------
    if data["roll_no"]:
        conn = get_db()
        if current_id is None:
            row = conn.execute(
                "SELECT id FROM students WHERE roll_no = ?", (data["roll_no"],)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM students WHERE roll_no = ? AND id != ?",
                (data["roll_no"], current_id),
            ).fetchone()
        if row is not None:
            errors.append(f"Roll number {data['roll_no']} is already in use.")

    return data, errors


def get_student_or_none(student_id):
    """Fetch one student row by id, or None if it does not exist."""
    return get_db().execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()


@students_bp.route("/")
def list_students():
    """Student list with optional search (name/roll) and course filter."""
    search = request.args.get("q", "").strip()
    course = request.args.get("course", "").strip()

    query = "SELECT * FROM students WHERE 1 = 1"
    params = []
    if search:
        query += " AND (name LIKE ? OR roll_no LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like])
    if course:
        query += " AND course = ?"
        params.append(course)
    query += " ORDER BY roll_no"

    students = get_db().execute(query, params).fetchall()
    return render_template(
        "students/list.html",
        students=students,
        search=search,
        course=course,
        courses=COURSES,
    )


@students_bp.route("/<int:student_id>")
def student_detail(student_id):
    """Detail page for a single student."""
    student = get_student_or_none(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students.list_students"))
    return render_template("students/detail.html", student=student)


@students_bp.route("/add", methods=["GET", "POST"])
def add_student():
    """Add form (GET) and create action (POST)."""
    if request.method == "POST":
        data, errors = validate_student(request.form)
        if errors:
            for error in errors:
                flash(error, "error")
            # Re-render the form with the values the user already typed.
            return (
                render_template(
                    "students/form.html", student=data, courses=COURSES, mode="add"
                ),
                400,
            )
        conn = get_db()
        conn.execute(
            INSERT_SQL,
            (
                data["roll_no"],
                data["name"],
                data["email"],
                data["phone"],
                data["course"],
                data["semester"],
                data["marks"],
            ),
        )
        conn.commit()
        flash(f"Student {data['name']} added successfully.", "success")
        return redirect(url_for("students.list_students"))
    return render_template(
        "students/form.html", student={}, courses=COURSES, mode="add"
    )


@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    """Edit form (GET, pre-filled) and update action (POST)."""
    student = get_student_or_none(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students.list_students"))

    if request.method == "POST":
        data, errors = validate_student(request.form, current_id=student_id)
        if errors:
            for error in errors:
                flash(error, "error")
            data["id"] = student_id  # form action URL needs the id
            return (
                render_template(
                    "students/form.html", student=data, courses=COURSES, mode="edit"
                ),
                400,
            )
        conn = get_db()
        conn.execute(
            "UPDATE students SET roll_no = ?, name = ?, email = ?, phone = ?,"
            " course = ?, semester = ?, marks = ? WHERE id = ?",
            (
                data["roll_no"],
                data["name"],
                data["email"],
                data["phone"],
                data["course"],
                data["semester"],
                data["marks"],
                student_id,
            ),
        )
        conn.commit()
        flash(f"Student {data['name']} updated successfully.", "success")
        return redirect(url_for("students.student_detail", student_id=student_id))

    return render_template(
        "students/form.html", student=student, courses=COURSES, mode="edit"
    )


@students_bp.route("/<int:student_id>/delete", methods=["GET", "POST"])
def delete_student(student_id):
    """Delete confirmation page (GET) and delete action (POST)."""
    student = get_student_or_none(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students.list_students"))

    if request.method == "POST":
        conn = get_db()
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        flash(f"Student {student['name']} deleted.", "success")
        return redirect(url_for("students.list_students"))

    return render_template("students/delete.html", student=student)
