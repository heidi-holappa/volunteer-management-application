from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randrange
from flask import session
from sqlalchemy.sql.elements import False_
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv

app = Flask(__name__)
# from dotenv import load_dotenv

# load_dotenv()
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    print(getenv("SECRET_KEY"))
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html", show=False)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/addnew", methods=["POST"])
def addnew():
    return render_template("addnew.html")

@app.route("/users")
def users():
    result = db.session.execute("SELECT * FROM tsohaproject.users WHERE role='volunteer'")
    # result = db.session.execute("SELECT users.lastname, users.role, users.firstname, users.user_id, users.email, string_agg(tasks.task, ', ') FROM tsohaproject.users, tsohaproject.volunteerqualification, tsohaproject.tasks WHERE users.user_id = volunteerqualification.user_id AND tasks.task_id = volunteerqualification.task_id GROUP BY users.lastname, users.firstname, users.role, users.user_id, users.email;")
    users = result.fetchall()
    print(users)
    return render_template("users.html", count=len(users), users=users)

@app.route("/submituser", methods=["POST"])
def submituser():
    lastname = request.form["lastname"]
    firstname = request.form["firstname"]
    email = request.form["email"]
    date = request.form["startdate"]
    role = request.form["role"]
    sql = "INSERT INTO tsohaproject.users (lastname, firstname, email, startdate, role) VALUES (:lastname, :firstname, :email, :startdate, :role)"
    db.session.execute(sql, {"lastname": lastname, "firstname":firstname, "email":email, "startdate":date, "role":role})
    db.session.commit()
    return redirect("/users")

@app.route("/view-user/<int:id>")
def viewuser(id):
    id = id
    sql1 = "SELECT * FROM tsohaproject.users WHERE user_id =:id;"
    result1 = db.session.execute(sql1, {"id":id})
    user = result1.fetchone()
    sql2 = "SELECT tasks.task  FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON users.user_id = volunteerqualification.user_id LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id WHERE users.user_id=:id"
    result2 = db.session.execute(sql2, {"id":id})
    qualifications = result2.fetchall()
    print(qualifications)
    return render_template("view-user.html", user=user, qualifications=qualifications)

@app.route("/edit-user/<int:id>", methods=["GET", "POST"])
def edituser(id):
    if request.method == "POST":
        id = id
        # Get basic information
        sql1 = "SELECT * FROM tsohaproject.users WHERE user_id =:id;"
        # Get qualifications
        sql2 = "SELECT tasks.task  FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON users.user_id = volunteerqualification.user_id LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id WHERE users.user_id=:id"
        # Get activityinformation
        sql3 = "SELECT activitylevel.level, currentactivity.date  FROM tsohaproject.users LEFT JOIN tsohaproject.currentactivity ON users.user_id = currentactivity.user_id LEFT JOIN tsohaproject.activitylevel on currentactivity.activity_id = activitylevel.activity_id WHERE users.user_id=:id"
        return render_template("edit-user.html")
    if request.method == "GET":
        return render_template("edit-user.html")

#This method validates an login attempt
@app.route("/auth/login", methods=["POST", "GET"])
def authlogin():
    error = False
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT users.user_id, password.password FROM tsohaproject.users, tsohaproject.password WHERE users.username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        if not user:
            error = True
        else:
            if check_password_hash(user.password, password):
                session["user_id"] = user.user_id
            else:
                error = True

    if error:
            return render_template("login.html", show=True, message="Username or password is incorrect. Please try again.")
    
    return redirect("/users")


            


#This method receives a new registration and coordinates/handles validation, saving to database and possible errors. 
@app.route("/auth/createadmin", methods=["POST"])
def createadmin():
    username = request.form["username"]
    password = request.form["password1"]
    password2 = request.form["password2"]
    hash_value = generate_password_hash(password)
    print(f"Hashvalue: {hash_value}")
    role = "admin"
    isactive = True
    #Password validation => Move to another module
    if len(password) < 8:
        return render_template("register.html", show=True, message="Password must be atleast 8 characters long.")
    if password != password2: 
        return render_template("register.html", show=True, message="Passwords do not match, try again.")
    #Try to commit given information to the database
    try:
        sqlusers = "INSERT INTO tsohaproject.users (username,role,isactive) VALUES (:username, :role, :isactive) RETURNING user_id"
        result = db.session.execute(sqlusers, {"username":username, "role":role, "isactive": isactive})
        user_id = result.fetchone()[0]
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        db.session.commit()
    except:
        return render_template("register.html", show=True, message="Something bad has happened, but I do not specifically know what. Try again.")
    
    return render_template("login.html", show=True, message="Registeration completed. Please login with your account.")


# @app.route("/send", methods=["POST"])
# def send():
#     content = request.form["content"]
#     sql = "INSERT INTO messages (content) VALUES (:content)"
#     db.session.execute(sql, {"content":content})
#     db.session.commit()
#     return redirect("/")
