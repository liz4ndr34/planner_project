import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required

# Flask application object
app = Flask(__name__)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# CS50 Library to use SQLite database
#db = SQL("sqlite://planner.db")
con = sqlite3.connect("planner.db", check_same_thread=False)
cursor = con.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
#Show user planner
    user_id = session["user_id"]

    #return render_template("", title = task["title"], period = task["period"], type = task["type"]) #sql table change

    con = sqlite3.connect("planner.db")
    cursor = con.cursor()

    cursor.execute("SELECT title, period, type, timestamp FROM tasks WHERE user_id = ? AND period ='Today' ORDER BY timestamp DESC", [user_id])
    tasks = cursor.fetchall()

    con.commit()
    cursor.close()
    print(tasks)
    
    return render_template("index.html", tasks=tasks) 

@app.route("/week")
@login_required
def week():
#Show user planner
    user_id = session["user_id"]

    con = sqlite3.connect("planner.db")
    cursor = con.cursor()

    cursor.execute("SELECT title, period, type, timestamp FROM tasks WHERE user_id = ? AND period ='Week' ORDER BY timestamp DESC", [user_id])
    weeks = cursor.fetchall()

    con.commit()
    cursor.close()
    
    return render_template("week.html", weeks=weeks)

@app.route("/month")
@login_required
def month():
#Show user planner
    user_id = session["user_id"]

    con = sqlite3.connect("planner.db")
    cursor = con.cursor()

    cursor.execute("SELECT title, period, type, timestamp FROM tasks WHERE user_id = ? AND period ='Month' ORDER BY timestamp DESC", [user_id])
    months = cursor.fetchall()

    con.commit()
    cursor.close()
    
    return render_template("month.html", months=months)

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("Must provide username", 403)

        elif not request.form.get("password"):
            flash("Must provide password", 403)

        # Query database for username
        con = sqlite3.connect("planner.db")
        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        rows = cursor.fetchall()
        
        con.commit()
        cursor.close()
        print(rows)
        # Check username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][4], request.form.get("password")):
            flash("invalid username and/or password", 403)

        session["user_id"] = rows[0][0]
        
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register users"""
    if request.method == "GET":
        return render_template("register.html")
    
    else:
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
    
        if not name:
            flash("Must provide name")

        if not username:
            flash("Must provide username")

        if not email:
            flash("Must provide email")

        if not password:
            flash("Must provide password")

        if not confirmation:
            flash("Must confirm password")

        if password != confirmation:
            flash("Passwords do not match")
        
        password_hash = generate_password_hash(password)

        try:
            con = sqlite3.connect("planner.db")
            cursor = con.cursor()

            sqlite_insert_query = """INSERT INTO users (name, username, email, hash) VALUES(?, ?, ?, ?)"""

            data_tuple = (name, username, email, password_hash)

            new_user = cursor.execute(sqlite_insert_query, data_tuple)
            con.commit()
            cursor.close()
    
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)

        finally:
            if con:
                con.close()
                print("The SQLite connection is closed")
                return redirect("/")
        
        session["user_id"] = new_user


@app.route("/plan", methods=["GET", "POST"])
@login_required
def plan():
    """Plan the task"""
    if request.method == "GET":
        return render_template("plan.html")
    
    else:
        title = request.form.get("title")
        period = request.form.get("period")
        type = request.form.get("type")

        if not title:
            flash("Must provide a title for the task")
        
        if not period:
            flash("Must provide a time period for the task")

        if not type:
            flash("Must provide a task type")

        user_id = session["user_id"]
        date = datetime.datetime.now()

        try:
            con = sqlite3.connect("planner.db")
            cursor = con.cursor()

            sqlite_insert_query_tasks = """INSERT INTO tasks (user_id, title, period, type, timestamp) VALUES (?, ?, ?, ?, ?)"""

            data_tuple_tasks = (user_id, title, period, type, date)

            cursor.execute(sqlite_insert_query_tasks, data_tuple_tasks)
            con.commit()
            cursor.close()

        except:
            flash("Task couldn't be added!")

        flash("Task added!")

        return redirect("/")

@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    user_id = session["user_id"]
    task_id = id
    print(task_id)

    if request.method == "GET":
        con = sqlite3.connect("planner.db")
        cursor = con.cursor()

        cursor.execute("SELECT title, period, type FROM tasks WHERE id = ? ", [id])
        tasks_period = cursor.fetchall()

        con.commit()
        cursor.close()    
        
        print(tasks_period)

        return render_template("update.html", periods = [row[1] for row in tasks_period], titles = [row[0] for row in tasks_period], types = [row[2] for row in tasks_period])

    else:        

        con = sqlite3.connect("planner.db")
        cursor = con.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", task_id)
        con.commit()
        con.close()

        flash("Task deleted!")
        return redirect("/")

