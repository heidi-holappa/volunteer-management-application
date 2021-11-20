from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randrange
from flask import session
from sqlalchemy.sql.elements import False_
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
import os
import re
import datetime

# TO-DO
# SPLIT INTO MULTIPLE FILES
# MAKE MORE FUNCTIONS THAT SERVE GENERAL PURPOSES
# CLEAN UP CODE
# CHECK WEB-APP'S TO-DO LISTS FOR ADDITIONAL TASKS


app = Flask(__name__)
# from dotenv import load_dotenv

# load_dotenv()
app.secret_key = getenv("SECRET_KEY")

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

#app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = uri
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

# TO-DO: CLEAN THIS AWAY
@app.route("/new")
def new():
    return render_template("new.html")

# TO-DO: CLEAN THIS AWAY
@app.route("/addnew", methods=["POST"])
def addnew():
    return render_template("addnew.html")

@app.route("/users")
def users():
    # result = db.session.execute("SELECT users.lastname, users.role, users.firstname, users.user_id, users.email, string_agg(tasks.task, ', ') FROM tsohaproject.users, tsohaproject.volunteerqualification, tsohaproject.tasks WHERE users.user_id = volunteerqualification.user_id AND tasks.task_id = volunteerqualification.task_id GROUP BY users.lastname, users.firstname, users.role, users.user_id, users.email;")
    # Info: check that user is authorized
    # TO-DO: CAN THIS BE MOVED TO A FUNCTION?
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    #Info: craft and execute SQL query
    result = db.session.execute("SELECT users.*, COUNT(messages.volunteer_id) AS activitycounter FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.volunteer_id) WHERE role='volunteer' GROUP BY users.user_id;")
    users = result.fetchall()
    print(users)
    return render_template("users.html", count=len(users), users=users)

def error(description):
    id = user_id()
    logged = False
    if id != 0:
        logged = True
    if description == 'notauthorized':
        message = "You have tried to access a page that you are not authorized to view. Please make sure you are logged in. If the problem continues, please leave feedback on the issue. Feedback form can be found in the footer"
    return render_template("error.html", error=message, logged=logged)


@app.route("/submituser", methods=["POST"])
def submituser():
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    lastname = request.form["lastname"]
    firstname = request.form["firstname"]
    email = request.form["email"]
    date = request.form["startdate"]
    role = request.form["role"]
    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]
        #Password validation => Move to another module
    if len(password) < 8:
        return render_template("addnew.html", show=True, message="Password must be atleast 8 characters long.")
    if password != password2: 
        return render_template("addnew.html", show=True, message="Passwords do not match, try again.")
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO tsohaproject.users (lastname, firstname, email, startdate, role, username) VALUES (:lastname, :firstname, :email, :startdate, :role, :username) RETURNING user_id"
        result = db.session.execute(sql, {"lastname": lastname, "firstname":firstname, "email":email, "startdate":date, "role":role, "username":username})
        user_id = result.fetchone()[0]
        qualifications = request.form.getlist("qualification")
        print(qualifications)
        for task_id in qualifications:
            if task_id != "":
                sql = "INSERT INTO tsohaproject.volunteerqualification (task_id, user_id) VALUES (:task_id, :user_id)"
                db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        db.session.commit()
    except:
        return render_template("register.html", show=True, message="Something bad has happened, but at this demo-stage I do not exactly know what. Try again.")
    return redirect("/users")

@app.route("/submit-message-volunteer/<int:id>", methods=["POST"])
def submit_message_volunteer(id):
    role = user_role()
    if role != 'volunteer':
        return error("notauthorized")
    date = request.form["date"]
    volunteer_id = id
    sender_id = id
    task_id = int(request.form["doneactivity"])
    content = request.form["content"] 
    print(f"DEF SUBMIT_MESSAGE_VOLUNTEER(ID): volunteer_id: {volunteer_id}, sender_id: {sender_id}, date: {date}, task_id: {task_id} content: {content}")
    try:
        sql="INSERT INTO tsohaproject.messages (volunteer_id, sender_id, task_id, activity_date, content) VALUES (:volunteer_id, :sender_id, :task_id, :activity_date, :content)"
        db.session.execute(sql, {"volunteer_id":volunteer_id, "sender_id":sender_id, "task_id":task_id, "activity_date":date, "content":content})
        db.session.commit()
    except:
        return render_template("volunteer-view", show=True, message="Something bad has happened, but at this demo-stage I do not exactly know what. Try again.")


    return redirect("/volunteer-view")

@app.route("/view-user/<int:id>")
def viewuser(id):
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    id = id
    user = get_userinfo(id)
    qualifications = get_qualifiations(id)
    print(qualifications)
    return render_template("view-user.html", user=user, qualifications=qualifications)

@app.route("/edit-user/<int:id>", methods=["GET", "POST"])
def edituser(id):
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    if request.method == "POST":
        id = id
        user = get_userinfo(id)
        qualifications = get_qualifiations(id)
        activity = get_activityinformation(id)
        return render_template("edit-user.html", user=user,  qualifications=qualifications, activity=activity)
    if request.method == "GET":
        return render_template("edit-user.html")



# Get qualifications
def get_qualifiations(id):
    # sql = "SELECT tasks.task_id, tasks.task  FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON users.user_id = volunteerqualification.user_id LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id WHERE users.user_id=:id"
    sql = "SELECT tasks.task, tasks.task_id, CASE WHEN tasks.task_id IN (SELECT tasks.task_id FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON (users.user_id = volunteerqualification.user_id) LEFT JOIN tsohaproject.tasks ON (volunteerqualification.task_id = tasks.task_id) WHERE users.user_id =:id) THEN true ELSE false END AS isqualified FROM tsohaproject.tasks"
    result = db.session.execute(sql, {"id":id})
    qualifications = result.fetchall()
    print(qualifications)
    return qualifications 

# Get basic userinformation from table users
def get_userinfo(id):
    sql1 = "SELECT * FROM tsohaproject.users WHERE user_id =:id"
    result1 = db.session.execute(sql1, {"id":id})
    user = result1.fetchone()
    return user

# Get activityinformation
def get_activityinformation(id):
    sql3 = "SELECT activitylevel.level, currentactivity.level_date  FROM tsohaproject.users LEFT JOIN tsohaproject.currentactivity ON users.user_id = currentactivity.user_id LEFT JOIN tsohaproject.activitylevel on currentactivity.activity_id = activitylevel.activity_id WHERE users.user_id=:id ORDER BY currentactivity.level_date DESC"
    result3 = db.session.execute(sql3, {"id":id})
    activity = result3.fetchall
    return activity


#This method validates an login attempt
@app.route("/auth/login", methods=["POST", "GET"])
def authlogin():
    # print("Hello world!")
    error = False
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT users.user_id, users.role, password.password FROM tsohaproject.users, tsohaproject.password WHERE users.username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        if not user:
            error = True
        else:
            if check_password_hash(user.password, password):
                session["user_id"] = user.user_id
                session["role"] = user.role
            else:
                error = True
    if error:
            return render_template("login.html", show=True, message="Username or password is incorrect. Please try again.")
    
    
    # A view for volunteers to post volunteer activities
    role = user_role()
    if role =='admin' or role == 'coordinator':
        return redirect("/users")
    else: 
        return redirect("/volunteer-view")

def user_id():
    id = session.get("user_id", 0)
    # print(f"user-id: {id}")
    return id

def role():
    role = session.get("role", 0)
    return role


def user_role():
    id = user_id()
    if (id != 0):
        sql = "SELECT role FROM tsohaproject.users WHERE user_id =:id"
        result = db.session.execute(sql, {"id":id})
        return result.fetchone()[0]
    else: 
        return id

@app.route("/logout")
def logout_and_redirect():
    logout()
    return redirect("/")


def logout():
    del session["user_id"]
    del session["role"]
    return

@app.route("/volunteer-view")
def volunteerview():
    role = user_role()
    if role != 'volunteer':
        return error("notauthorized")
    id = user_id()
    # Get basic information
    sql = "SELECT * FROM tsohaproject.users WHERE user_id =:id"
    result = db.session.execute(sql, {"id":id})
    user = result.fetchone()
    # Get volunteer's activities - volunteer can participate in activities they are qualified in
    sql2 = "SELECT tasks.task_id, tasks.task  FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON users.user_id = volunteerqualification.user_id LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id WHERE users.user_id=:id"
    result2 = db.session.execute(sql2, {"id":id})
    activities = result2.fetchall()
    sql3 = "SELECT messages.activity_date, messages.content, tasks.task FROM tsohaproject.messages LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) WHERE messages.volunteer_id=:id ORDER BY messages.activity_date DESC" 
    result3 = db.session.execute(sql3, {"id":id})
    messages = result3.fetchall()
    print(messages)
    if len(messages) == 0:
        nomessages = True
    else:
        nomessages = False
    print(nomessages)
    return render_template("volunteer-view.html", user=user, activities=activities, messages=messages, nomessages=nomessages)


#This method receives a new registration and coordinates/handles validation, saving to database and possible errors. 
@app.route("/auth/createadmin", methods=["POST"])
def createadmin():
    username = request.form["username"]
    password = request.form["password1"]
    password2 = request.form["password2"]
    role = "admin"
    isactive = True
    #Password validation => Move to another module
    if len(password) < 8:
        return render_template("register.html", show=True, message="Password must be atleast 8 characters long.")
    if password != password2: 
        return render_template("register.html", show=True, message="Passwords do not match, try again.")
    hash_value = generate_password_hash(password)
    # print(f"Hashvalue: {hash_value}")
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

@app.route("/docs/aboutus")
def about_us():
    id = user_id()
    print(id)
    logged = False
    if id != 0:
        logged = True
    return render_template("docs/aboutus.html", logged=logged)

@app.route("/docs/feedback")
def feedback():
    id = user_id()
    print(id)
    logged = False
    if id != 0:
        logged = True
    return render_template("docs/feedback.html", logged=logged)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    content = request.form["content"]
    now = datetime.date.today()
    print(now)
    return render_template("/docs/thank-you.html")

    
@app.route("/view-activities")
def supervisor_view_activities():
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    sql = "SELECT users.lastname, users.firstname, messages.msg_id, messages.activity_date, messages.content, tasks.task FROM tsohaproject.users INNER JOIN tsohaproject.messages ON (users.user_id = messages.volunteer_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) ORDER BY messages.activity_date DESC" 
    result = db.session.execute(sql)
    messages = result.fetchall()
    print(messages)
    if len(messages) == 0:
        nomessages = True
    else:
        nomessages = False
    print(nomessages)
    return render_template("message-view.html", messages=messages, nomessages=nomessages)


# TO-DO: CLEAN THIS AWAY
# @app.route("/send", methods=["POST"])
# def send():
#     content = request.form["content"]
#     sql = "INSERT INTO messages (content) VALUES (:content)"
#     db.session.execute(sql, {"content":content})
#     db.session.commit()
#     return redirect("/")
