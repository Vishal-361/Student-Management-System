"""
Student Management System - application entry point.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os

from flask import Flask, redirect, url_for

import db
from students.routes import students_bp


def create_app():
    """Application factory: builds and configures the Flask app."""
    app = Flask(__name__)

    # Secret key is only used to sign the session cookie (flash messages).
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    # SQLite database file lives inside Flask's instance folder.
    app.config["DATABASE"] = os.path.join(app.instance_path, "students.db")

    # Make sure the instance folder exists before SQLite tries to use it.
    os.makedirs(app.instance_path, exist_ok=True)

    # Close the per-request database connection when the request ends.
    app.teardown_appcontext(db.close_db)

    # Create the tables and seed sample data on first run.
    with app.app_context():
        db.init_db()

    # Modular routing: every student page lives in the students blueprint.
    app.register_blueprint(students_bp)

    @app.route("/")
    def home():
        # The home page simply forwards to the student list.
        return redirect(url_for("students.list_students"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
