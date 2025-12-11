from flask import Flask, render_template, request, redirect, session
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                priority TEXT,
                deadline TEXT,
                status TEXT)""")
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        return "Invalid Credentials"
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        priority = request.form["priority"]
        deadline = request.form["deadline"]

        c.execute("INSERT INTO tasks (user_id, title, priority, deadline, status) VALUES (?, ?, ?, ?, ?)",
                  (session["user_id"], title, priority, deadline, "Pending"))
        conn.commit()

    c.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],))
    tasks = c.fetchall()

    conn.close()

    return render_template("dashboard.html", tasks=tasks)

@app.route("/update/<int:task_id>")
def update(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
