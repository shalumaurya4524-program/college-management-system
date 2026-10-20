from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-demo-secret"
DB_PATH = Path(__file__).with_name("college.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT NOT NULL,
            year TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            credits INTEGER NOT NULL DEFAULT 3
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
            UNIQUE(student_id, date),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL CHECK(marks BETWEEN 0 AND 100),
            semester TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """)
        if db.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO students (roll_no,name,email,department,year) VALUES (?,?,?,?,?)",
                [
                    ("IT202501", "Shalu Maurya", "shalu@example.com", "Information Technology", "2nd Year"),
                    ("IT202502", "Rahul Singh", "rahul@example.com", "Information Technology", "2nd Year"),
                    ("CS202503", "Priya Verma", "priya@example.com", "Computer Science", "3rd Year"),
                ],
            )
        if db.execute("SELECT COUNT(*) FROM faculty").fetchone()[0] == 0:
            db.executemany("INSERT INTO faculty(name,email,department) VALUES (?,?,?)", [
                ("Anita Sharma", "anita@example.com", "Information Technology"),
                ("Rakesh Singh", "rakesh@example.com", "Computer Science"),
            ])
        if db.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            db.executemany("INSERT INTO courses(code,name,department,credits) VALUES (?,?,?,?)", [
                ("IT201", "Data Structures", "Information Technology", 4),
                ("IT202", "Database Management Systems", "Information Technology", 4),
                ("CS201", "Operating Systems", "Computer Science", 3),
            ])

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # Demo credentials only; replace with hashed user accounts for real deployment.
        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password. Use the demo credentials shown below.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        counts = {
            "students": db.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "faculty": db.execute("SELECT COUNT(*) FROM faculty").fetchone()[0],
            "courses": db.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
            "attendance": db.execute("SELECT COUNT(*) FROM attendance WHERE date = date('now','localtime') AND status='Present'").fetchone()[0],
        }
        recent = db.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("dashboard.html", counts=counts, recent=recent)

@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    with get_db() as db:
        if request.method == "POST":
            action = request.form.get("action", "add")
            if action == "delete":
                db.execute("DELETE FROM students WHERE id=?", (request.form.get("id"),))
                flash("Student deleted.", "success")
            elif action == "edit":
                try:
                    db.execute("""UPDATE students SET roll_no=?,name=?,email=?,department=?,year=? WHERE id=?""",
                        (request.form["roll_no"].strip(), request.form["name"].strip(),
                         request.form.get("email","").strip(), request.form["department"],
                         request.form["year"], request.form["id"]))
                    flash("Student updated.", "success")
                except sqlite3.IntegrityError:
                    flash("Roll number already exists.", "error")
            else:
                try:
                    db.execute("""INSERT INTO students(roll_no,name,email,department,year) VALUES(?,?,?,?,?)""",
                        (request.form["roll_no"].strip(), request.form["name"].strip(),
                         request.form.get("email","").strip(), request.form["department"], request.form["year"]))
                    flash("Student added successfully.", "success")
                except sqlite3.IntegrityError:
                    flash("Roll number already exists. Please use a unique roll number.", "error")
            return redirect(url_for("students"))
        rows = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return render_template("students.html", students=rows)

@app.route("/faculty", methods=["GET", "POST"])
@login_required
def faculty():
    with get_db() as db:
        if request.method == "POST":
            if request.form.get("action") == "delete":
                db.execute("DELETE FROM faculty WHERE id=?", (request.form.get("id"),))
                flash("Faculty member deleted.", "success")
            else:
                db.execute("INSERT INTO faculty(name,email,department) VALUES(?,?,?)",
                    (request.form["name"].strip(), request.form.get("email","").strip(), request.form["department"]))
                flash("Faculty member added.", "success")
            return redirect(url_for("faculty"))
        rows = db.execute("SELECT * FROM faculty ORDER BY id DESC").fetchall()
    return render_template("faculty.html", faculty=rows)

@app.route("/courses", methods=["GET", "POST"])
@login_required
def courses():
    with get_db() as db:
        if request.method == "POST":
            if request.form.get("action") == "delete":
                db.execute("DELETE FROM courses WHERE id=?", (request.form.get("id"),))
                flash("Course deleted.", "success")
            else:
                try:
                    db.execute("INSERT INTO courses(code,name,department,credits) VALUES(?,?,?,?)",
                        (request.form["code"].strip().upper(), request.form["name"].strip(),
                         request.form["department"], int(request.form["credits"])))
                    flash("Course added.", "success")
                except sqlite3.IntegrityError:
                    flash("Course code already exists.", "error")
            return redirect(url_for("courses"))
        rows = db.execute("SELECT * FROM courses ORDER BY id DESC").fetchall()
    return render_template("courses.html", courses=rows)

@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    with get_db() as db:
        if request.method == "POST":
            try:
                db.execute("""INSERT INTO attendance(student_id,date,status) VALUES(?,?,?)
                    ON CONFLICT(student_id,date) DO UPDATE SET status=excluded.status""",
                    (request.form["student_id"], request.form["date"], request.form["status"]))
                flash("Attendance saved.", "success")
            except sqlite3.IntegrityError:
                flash("Please select a valid student.", "error")
            return redirect(url_for("attendance"))
        students_list = db.execute("SELECT id,roll_no,name FROM students ORDER BY name").fetchall()
        rows = db.execute("""SELECT a.*,s.name,s.roll_no FROM attendance a
            JOIN students s ON s.id=a.student_id ORDER BY a.date DESC,a.id DESC LIMIT 100""").fetchall()
    return render_template("attendance.html", students=students_list, attendance=rows)

@app.route("/results", methods=["GET", "POST"])
@login_required
def results():
    with get_db() as db:
        if request.method == "POST":
            try:
                marks = int(request.form["marks"])
                if not 0 <= marks <= 100:
                    raise ValueError
                db.execute("INSERT INTO results(student_id,subject,marks,semester) VALUES(?,?,?,?)",
                    (request.form["student_id"], request.form["subject"].strip(), marks, request.form["semester"]))
                flash("Result saved.", "success")
            except (ValueError, sqlite3.IntegrityError):
                flash("Enter marks between 0 and 100 and select a valid student.", "error")
            return redirect(url_for("results"))
        students_list = db.execute("SELECT id,roll_no,name FROM students ORDER BY name").fetchall()
        rows = db.execute("""SELECT r.*,s.name,s.roll_no FROM results r
            JOIN students s ON s.id=r.student_id ORDER BY r.id DESC""").fetchall()
    return render_template("results.html", students=students_list, results=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
