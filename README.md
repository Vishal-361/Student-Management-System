# Student Management System

A full-stack CRUD web application for managing student records, built with
**Flask** and **SQLite**. It uses modular routing (a Flask Blueprint) and
server-side input validation, with a clean hand-written HTML/CSS interface.

## Features

- **Full CRUD** - add, view, edit and delete student records
  (roll number, name, email, phone, course, semester, marks)
- **Search** students by name or roll number
- **Filter** the list by course
- **Detail view** for every student
- **Delete confirmation** page before a record is removed
- **Server-side validation** - required fields, email format, phone digits,
  semester (1-8) and marks (0-100) ranges, unique roll numbers - with
  flash messages for errors and successes
- **Auto-setup** - the SQLite database is created and seeded with 8 sample
  students on first run, so the app demos instantly

## Tech Stack

- **Python 3**
- **Flask** (routing, Jinja2 templates, flash messages)
- **SQLite** via Python's built-in `sqlite3` module (no ORM)
- **HTML + CSS** (hand-written stylesheet, no framework)

## Setup & Run

```bash
# 1. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

The database file (`instance/students.db`) is created automatically on the
first run. Delete it and restart the app to reset the sample data.

## Project Structure

```
Student-Management-System/
├── app.py                  # Entry point - app factory, blueprint registration
├── db.py                   # SQLite helpers: connection, schema, seed data
├── students/
│   ├── __init__.py
│   └── routes.py           # Blueprint with all student routes + validation
├── templates/
│   ├── base.html           # Shared layout (header, footer, flash messages)
│   └── students/
│       ├── list.html       # List view with search & course filter
│       ├── detail.html     # Single student detail view
│       ├── form.html       # Shared add / edit form
│       └── delete.html     # Delete confirmation page
├── static/
│   └── style.css           # Hand-written stylesheet
├── requirements.txt
└── README.md
```

## How It Works

- `app.py` builds the app with an **application factory**, creates the
  database on startup, and registers the `students` blueprint - the app
  itself contains no page logic.
- `students/routes.py` holds every student page in one **Blueprint**, which
  keeps routing modular and easy to extend.
- `db.py` opens one SQLite connection per request (stored on Flask's `g`)
  and closes it automatically when the request ends.
- All form input is validated **on the server** in `validate_student()`
  before anything touches the database; SQL queries use parameterised
  placeholders throughout.
