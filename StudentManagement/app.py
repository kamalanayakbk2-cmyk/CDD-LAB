
from flask import Flask, render_template_string, request, redirect, url_for, flash
import mysql.connector
import os
import time

app = Flask(__name__)
app.secret_key = "student-management-secret-key"


def get_db_connection():
    for attempt in range(10):
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER", "appuser"),
                password=os.getenv("DB_PASSWORD", "apppass"),
                database=os.getenv("DB_NAME", "studentdb")
            )
            return connection

        except mysql.connector.Error as error:
            print("Waiting for MySQL:", error)
            time.sleep(3)

    raise Exception("Unable to connect to MySQL database")


HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f2f4f8;
            margin: 40px;
        }

        h1 {
            text-align: center;
            color: #243b55;
        }

        .container {
            background: white;
            padding: 25px;
            border-radius: 12px;
            max-width: 1000px;
            margin: auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        input {
            padding: 10px;
            margin: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        button, .edit-btn {
            padding: 9px 14px;
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            text-decoration: none;
        }

        .add-btn {
            background: #198754;
        }

        .search-btn {
            background: #0d6efd;
        }

        .edit-btn {
            background: #f0ad4e;
        }

        .delete-btn {
            background: #dc3545;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
        }

        th {
            background: #243b55;
            color: white;
        }

        tr:nth-child(even) {
            background: #f2f4f8;
        }

        .message {
            color: green;
            text-align: center;
        }

        .actions {
            display: flex;
            justify-content: center;
            gap: 8px;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>Student Management System</h1>

    <h2>Add New Student</h2>

    <form action="/add" method="POST">
        <input type="text" name="name"
               placeholder="Student Name" required>

        <input type="text" name="department"
               placeholder="Department" required>

        <button class="add-btn" type="submit">
            Add Student
        </button>
    </form>

    <h2>Search Students</h2>

    <form action="/" method="GET">
        <input type="text" name="search"
               placeholder="Search by name or department"
               value="{{ search }}">

        <button class="search-btn" type="submit">
            Search
        </button>

        <a href="/">Show All</a>
    </form>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p class="message">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <h2>Student Details</h2>

    <table>
        <tr>
            <th>ID</th>
            <th>Student Name</th>
            <th>Department</th>
            <th>Actions</th>
        </tr>

        {% for student in students %}
        <tr>
            <td>{{ student.id }}</td>
            <td>{{ student.name }}</td>
            <td>{{ student.department }}</td>

            <td>
                <div class="actions">

                    <a class="edit-btn"
                       href="/edit/{{ student.id }}">
                       Edit
                    </a>

                    <form action="/delete/{{ student.id }}"
                          method="POST"
                          onsubmit="return confirm('Delete this student?');">

                        <button class="delete-btn" type="submit">
                            Delete
                        </button>

                    </form>

                </div>
            </td>
        </tr>
        {% endfor %}

    </table>

    {% if not students %}
        <p>No students found.</p>
    {% endif %}

</div>

</body>
</html>
"""


EDIT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Student</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f4f8;
            padding: 40px;
        }

        .container {
            background: white;
            padding: 30px;
            max-width: 450px;
            margin: auto;
            border-radius: 10px;
        }

        input {
            width: 95%;
            padding: 10px;
            margin: 10px 0;
        }

        button {
            background: #198754;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>Edit Student</h1>

    <form method="POST">

        <label>Student Name</label>
        <input type="text" name="name"
               value="{{ student.name }}" required>

        <label>Department</label>
        <input type="text" name="department"
               value="{{ student.department }}" required>

        <button type="submit">Update Student</button>

    </form>

    <br>

    <a href="/">Back to Home</a>

</div>

</body>
</html>
"""


@app.route("/")
def home():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:
        cursor.execute(
            "SELECT * FROM students WHERE name LIKE %s OR department LIKE %s",
            (f"%{search}%", f"%{search}%")
        )
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template_string(
        HOME_HTML,
        students=students,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()

    if not name or not department:
        flash("Please enter both name and department.")
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

        if name and department:
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

    if student is None:
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

    cursor.close()
    connection.close()

    flash("Student deleted successfully!")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
