import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db= SQL("sqlite:///appointments.db")


def massage(massage):
    return render_template("massage.html", massage=massage)

@app.route("/", methods=["GET", "POST"])
def index():
    #take bussines names
    users = db.execute("SELECT bussines,id FROM users")
    return render_template ("index.html", users=users)


@app.route("/add", methods=["GET", "POST"])
def add():
    # take info from customers
    if request.method == "POST":
        name = request.form.get("name")
        number = request.form.get("number")
        date = request.form.get("date")
        Description = request.form.get("Description")
        user_id = request.form.get("id")

        # trying to insert value
        try:
            db.execute("INSERT INTO appointments ( name, number, date, Description, user_id) VALUES (?,?,?,?,?)", name, number, date, Description, user_id)
            return massage("appointment add succesfull. thank you:)")
        except:
            #check for why undone
            notunique = db.execute("SELECT * FROM appointments WHERE date = ?", date)
            if notunique:
                return massage("appointment already taked")
            else:
                return massage("unsuccess. try agein!")
    else :
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):

            return massage("name is empty")

        # Ensure password was submitted
        elif not request.form.get("password"):

            return massage("pssword is empty")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):

            return massage("invalid username and/or password")

        #select values from list
        try:
            appointments = db.execute("SELECT * FROM appointments WHERE user_id = ?", rows[0]["id"])
            # send user to list
            return render_template("list.html", appointments=appointments)
        except:
            return massage("error. pleas call backups")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    #register user
    if (request.method == "POST"):
        username = request.form.get('username')
        bussines = request.form.get("bussines")
        number = request.form.get("number")
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            return massage("invalide username")
        elif not password:
            return massage("invalide password")
        elif not confirmation:
            return massage("invalide confirmation")

        if password != confirmation:
            return massage("password and confirmation not same")

        hash = generate_password_hash(password)
        try :
            db.execute("INSERT INTO users (username,hash,bussines,number) VALUES (?,?,?,?)", username, hash, bussines, number)
            return redirect('/')
        except:
            return massage("unsuccess. try agian")

    else:
        return render_template("register.html")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if (request.method == "POST"):
        id = request.form.get("id")
        if id:
            try:
                appointments = db.execute("SELECT user_id FROM appointments WHERE id = ?", id)
                db.execute("DELETE FROM appointments WHERE id = ?", id)
                return render_template("list.html", appointments=appointments)
            except:
                return massage("unsuccess. try again")
        else:
            return massage("ERROR. pleas call backups")
    else:
        return render_template("login.html")
