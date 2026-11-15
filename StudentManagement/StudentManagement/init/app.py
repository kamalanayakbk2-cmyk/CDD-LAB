
from flask import Flask, render_template_string, request, redirect, url_for, flash
import mysql.connector
import os
import time

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "student-management-secret")


def get_db_connection():
    for attempt in range(10):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER", "appuser"),
                password=os.getenv("DB_PASSWORD", "apppass"),
                database=os.getenv("DB_NAME", "studentdb")
            )
        except mysql.connector.Error as error:
            print("Waiting for MySQL:", error)
            time.sleep(3)

    raise RuntimeError("Unable to connect to MySQL")


@app.route("/")
def home():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:
        cursor.execute(
            "SELECT * FROM students WHERE name LIKE %s OR department LIKE %s ORDER BY id",
            (f"%{search}%", f"%{search}%")
        )
    else:
        cursor.execute("SELECT * FROM students ORDER BY id")

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template_string(HTML, students=students, search=search)


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()

    if not name or not department:
        flash("Please fill in all fields.")
        return redirect(url_for("home"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO students (name, department) VALUES (%s, %s)",
        (name, department)
    )

    connection.commit()
    cursor.close()
    connection.close()

    flash("Student added successfully!")
    return redirect(url_for("home"))


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not department:
            cursor.close()
            connection.close()
            flash("Please fill in all fields.")
            return redirect(url_for("edit_student", student_id=student_id))

        cursor.execute(
            "UPDATE students SET name=%s, department=%s WHERE id=%s",
            (name, department, student_id)
        )

        connection.commit()
        cursor.close()
        connection.close()

        flash("Student updated successfully!")
        return redirect(url_for("home"))

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (student_id,)
    )
    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if not student:
        flash("Student not found.")
        return redirect(url_for("home"))

    return render_template_string(EDIT_HTML, student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=%s",
        (student_id,)
    )

    connection.commit()
    deleted = cursor.rowcount

    cursor.close()
    connection.close()

    flash("Student deleted successfully!" if deleted else "Student not found.")
    return redirect(url_for("home"))


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Management System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px;
            color: #1e293b;
        }
        .container {
            max-width: 950px;
            margin: auto;
        }
        h1 { color: #173b70; }
        .card {
            background: white;
            padding: 22px;
            border-radius: 12px;
            margin-bottom: 22px;
            box-shadow: 0 3px 12px #0000000d;
        }
        input {
            padding: 11px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            margin: 5px;
        }
        button, .edit {
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            background: #2563eb;
            color: white;
        }
        .delete { background: #dc2626; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 14px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
        }
        th { background: #eff6ff; }
        .message { color: #15803d; }
        .search { margin-bottom: 15px; }
        @media(max-width: 600px) {
            body { padding: 12px; }
            input { max-width: 90%; }
            table { font-size: 13px; }
            th, td { padding: 8px; }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Student Management System</h1>
    <p>Manage student records easily</p>

    {% with messages = get_flashed_messages() %}
      {% for message in messages %}
        <p class="message">{{ message }}</p>
      {% endfor %}
    {% endwith %}

    <div class="card">
        <h2>Add New Student</h2>
        <form action="/add" method="POST">
            <input type="text" name="name"
                   placeholder="Student Name" required>
            <input type="text" name="department"
                   placeholder="Department" required>
            <button type="submit">Add Student</button>
        </form>
    </div>

    <div class="card">
        <h2>Student Records</h2>

        <form class="search" method="GET" action="/">
            <input type="text" name="search"
                   placeholder="Search name or department"
                   value="{{ search }}">
            <button type="submit">Search</button>
            <a href="/">Clear</a>
        </form>

        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Actions</th>
            </tr>

            {% for student in students %}
            <tr>
                <td>{{ student.id }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.department }}</td>
                <td>
                    <a class="edit"
                       href="/edit/{{ student.id }}">Edit</a>

                    <form action="/delete/{{ student.id }}"
                          method="POST" style="display:inline;"
                          onsubmit="return confirm('Delete this student?');">
                        <button class="delete" type="submit">
                            Delete
                        </button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="4">No students found.</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</div>
</body>
</html>
"""


EDIT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Student</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            padding: 30px;
        }
        .card {
            background: white;
            max-width: 450px;
            margin: 50px auto;
            padding: 25px;
            border-radius: 12px;
        }
        input {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            margin: 10px 0;
        }
        button {
            padding: 12px 18px;
            background: #2563eb;
            color: white;
            border: 0;
            border-radius: 6px;
        }
    </style>
</head>
<body>
<div class="card">
    <h2>Edit Student Details</h2>
    <form method="POST">
        <label>Student Name</label>
        <input type="text" name="name"
               value="{{ student.name }}" required>

        <label>Department</label>
        <input type="text" name="department"
               value="{{ student.department }}" required>

        <button type="submit">Update Student</button>
        <a href="/">Cancel</a>
    </form>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
