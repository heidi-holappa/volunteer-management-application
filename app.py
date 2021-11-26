# To be refactored
from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randrange
from flask import session
from sqlalchemy.sql.elements import False_, Null
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
import os
import re
from datetime import datetime, date, timezone


# TO-DO
# SPLIT INTO MULTIPLE FILES (REFACTOR)
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
    """Render landing page"""
    print(getenv("SECRET_KEY"))
    return render_template("index.html")

@app.route("/login")
def login():
    """Render login page"""
    return render_template("login.html")

@app.route("/register")
def register():
    """Render registration page"""
    return render_template("register.html", show=False)

@app.route("/new")
def new():
    """TO-DO: CLEAN THIS AWAY"""
    return render_template("new.html")

@app.route("/addnew", methods=["POST"])
def addnew():
    """TO-DO: CLEAN THIS AWAY"""
    return render_template("addnew.html")

@app.route("/users")
def view_users():
    """Fetch userinformation and show user table"""
    # Info: check that user is authorized
    # TO-DO: CAN THIS BE MOVED TO A FUNCTION?
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    #Info: craft and execute SQL query
    #TO-DO: Select columns instead of *
    sql = "SELECT users.*, COUNT(messages.sender_id) AS activitycounter \
        FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) \
        WHERE role='volunteer' AND isactive='true' \
        GROUP BY users.user_id;"
    result = db.session.execute(sql)
    users = result.fetchall()
    print(users)
    return render_template("users.html", count=len(users), users=users)

def error(description):
    """Render Error view"""
    u_id = get_user_id()
    logged = False
    if u_id != 0:
        logged = True
    if description == 'notauthorized':
        message = ('You have tried to access a page that you are not authorized to view. \
            Please make sure you are logged in. If the problem continues, \
                please leave feedback on the issue. Feedback form can be found in the footer.')
    return render_template("error.html", error=message, logged=logged)

#TO-DO: Function too long. This how to split. 
@app.route("/submituser", methods=["POST"])
def submituser():
    """Add a new user"""
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    lastname = request.form["lastname"]
    firstname = request.form["firstname"]
    email = request.form["email"]
    startdate = request.form["startdate"]
    # Had to juggle a bit with a 'selected disabled' form element. Solved the issue with try.
    #TO-DO: Check in weekly guidance whether this is a good practice for using try
    try:
        role = request.form["role"]
    except:
        role = None
    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]
    params = [lastname, firstname, email, date, role, username]
    # Check that all fields have information
    for i in params:
        if i is None or len(i) == 0:
            return render_template("addnew.html", \
                show=True, message="One of the fields was empty. \
                    Please carefully fill in all fields.", \
                    filled=params)
    qualifications = request.form.getlist("qualification")
    noqualifications = True
    for qualification in qualifications:
        if qualification != "":
            noqualifications = False
    if noqualifications:
        return render_template("addnew.html", \
            show=True, message="Please select \
                atleast one qualification.", filled=params)
    # Create default values for a new user
    isactive = True
    activitylevel = 4
    #Password validation => TO-DO: Move to another module
    if len(password) < 8:
        return render_template("addnew.html", \
            show=True, message="Password must be atleast \
                8 characters long.", filled=params)
    if password != password2:
        return render_template("addnew.html", \
            show=True, message="Passwords do not \
                match, try again.", filled=params)
    hash_value = generate_password_hash(password)
    #Try is used here because one of the tables (users) has an unique column (username).
    #The commit contains multiple interts.
    try:
        sql = """INSERT INTO tsohaproject.users (lastname, firstname, email,
                startdate, role, username, isactive) 
                VALUES (:lastname, :firstname, :email, 
                :startdate, :role, :username, :isactive) 
                RETURNING user_id"""
        result = db.session.execute(sql, {"lastname": lastname, "firstname":firstname, \
            "email":email, "startdate":startdate, "role":role, "username":username, "isactive":isactive})
        user_id = result.fetchone()[0]
        print(qualifications)
        for task_id in qualifications:
            if task_id != "":
                sql = "INSERT INTO tsohaproject.volunteerqualification (task_id, user_id) \
                    VALUES (:task_id, :user_id)"
                db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) \
            VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        sqlactivity = "INSERT INTO tsohaproject.currentactivity (level_date, user_id, activity_id) \
            VALUES (:level_date, :user_id, :activitylevel)"
        db.session.execute(sqlactivity, {"level_date":startdate, "user_id":user_id, \
            "activitylevel":activitylevel})
        db.session.commit()
    except:
        return render_template("addnew.html", show=True, \
            message="Something bad has happened, but at this demo-stage I do not exactly \
                know what. Most likely the username was already taken. Try again."\
                    , filled=params)
    return redirect("/users")

@app.route("/submit-message-volunteer/<int:id>", methods=["POST"])
def submit_message_volunteer(u_id):
    """This function stores a new message."""
    role = user_role()
    if role != 'volunteer':
        return error("notauthorized")
    date = request.form["date"]
    sender_id = u_id
    volunteer_id = u_id
    task_id = int(request.form["doneactivity"])
    content = request.form["content"]
    msg_sent = datetime.now(timezone.utc)
    # print(msg_sent)
    # print(f"DEF SUBMIT_MESSAGE_VOLUNTEER(ID): sender_id: {sender_id}, date: \
    # {date}, task_id: {task_id} content: {content}, msg_sent: {msg_sent}")
    #TO-DO: This is not a recommended way of using a try. Fix this.
    try:
        sql = "INSERT INTO tsohaproject.messages (volunteer_id, sender_id, task_id, activity_date, \
            send_date, content) \
            VALUES (:volunteer_id, :sender_id, :task_id, :activity_date, :send_date, :content) \
            RETURNING msg_id"
        result = db.session.execute(sql, {"volunteer_id":volunteer_id, "sender_id":sender_id, \
            "task_id":task_id, "activity_date":date, "send_date":msg_sent, "content":content})
        msg_id = result.fetchone()[0]
        sql_update = "UPDATE tsohaproject.messages SET thread_id=:msg_id WHERE msg_id=:msg_id"
        db.session.execute(sql_update, {"msg_id":msg_id})
        db.session.commit()
    except:
        return render_template("volunteer-view", show=True, message="Something bad has happened, \
            but at this demo-stage I do not exactly know what. Try again.")
    return redirect("/volunteer-view")

@app.route("/update-user/<int:id>", methods=["POST"])
def update_user(u_id):
    """Old userinfo is fetched from database and updated for those fields that can be updated."""
    user_id = u_id
    # Get basic information TO-DO: REPLACE * WITH COLUMNS NEEDED!
    sql = "SELECT * FROM tsohaproject.users WHERE user_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    oldinfo = result.fetchone()
    lastname = request.form["lastname"]
    firstname = request.form["firstname"]
    email = request.form["email"]
    phone = request.form["phone"]
    startdate = request.form["startdate"]
    role = request.form["role"]
    username = request.form["username"]
    isactive = True
    if request.form.get("terminate") != None:
        isactive = False
    if not isactive:
        enddate = date.today()
        print(enddate)
    else:
        enddate = None
    newinfo = [oldinfo[0], role, lastname, firstname, username, email, phone, \
        startdate, enddate, oldinfo[9], isactive]
    # for i in oldinfo:
    #     print(i)
    # for j in newinfo:
    #     print(j)
    try:
        sql = "UPDATE tsohaproject.users \
            SET role=:role, lastname=:lastname, firstname=:firstname, username=:username, email=:email, \
                phone=:phone, startdate=:startdate, enddate=:enddate, basictraining=:basictraning, isactive=:isactive \
            WHERE user_id=:user_id"
        db.session.execute(sql, {"role":newinfo[1], "lastname":newinfo[2], "firstname":newinfo[3], \
            "username":newinfo[4], "email":newinfo[5], "phone":newinfo[6], "startdate":newinfo[7], \
            "enddate":newinfo[8], "basictraning":newinfo[9], "isactive":newinfo[10], \
            "user_id":user_id})
        db.session.commit()
    except:
        return render_template("error.html", logged=True, error="Something bad has happened, \
            but at this demo-stage I do not exactly know what. Try again.")
    if not isactive:
        return redirect("/users")
    return redirect("/view-user/" + str(user_id))

@app.route("/view-user/<int:id>")
def viewuser(u_id):
    """Render singe user's informationpage"""
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    user = get_userinfo(u_id)
    qualifications = get_qualifiations(u_id)
    currentactivity = get_currentactivity(u_id)
    trainings = get_additionaltrainings(u_id)
    tools = get_loanedtools(u_id)
    return render_template("view-user.html", user=user, qualifications=qualifications, \
        currentactivity=currentactivity, trainings=trainings, tools=tools)

# TO-DO - see why post? Shouldn't it be GET?
@app.route("/edit-user/<int:id>", methods=["GET", "POST"])
def edituser(u_id):
    """Render edit-user page"""
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    if request.method == "POST":
        user = get_userinfo(u_id)
        qualifications = get_qualifiations(u_id)
        activity = get_activityinformation(u_id)
        return render_template("edit-user.html", user=user, \
            qualifications=qualifications, activity=activity)
    if request.method == "GET":
        return render_template("edit-user.html")

def get_qualifiations(u_id):
    """Return qualifications"""
    # sql = "SELECT tasks.task_id, tasks.task  \
    # FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification \
    # ON users.user_id = volunteerqualification.user_id \
    # LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id \
    # WHERE users.user_id=:id"
    sql = "SELECT tasks.task, tasks.task_id, CASE \
        WHEN tasks.task_id IN (SELECT tasks.task_id \
        FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification \
        ON (users.user_id = volunteerqualification.user_id) \
        LEFT JOIN tsohaproject.tasks ON (volunteerqualification.task_id = tasks.task_id) \
        WHERE users.user_id =:id) \
        THEN true ELSE false END AS isqualified \
        FROM tsohaproject.tasks"
    result = db.session.execute(sql, {"id":u_id})
    qualifications = result.fetchall()
    print(qualifications)
    return qualifications

def get_additionaltrainings(u_id):
    """Return additional trainings participated in"""
    sql = "SELECT additionaltrainings.training, trainingparticipation.training_date \
        FROM tsohaproject.trainingparticipation LEFT JOIN tsohaproject.additionaltrainings \
        ON (trainingparticipation.training_id = additionaltrainings.training_id) \
        WHERE user_id =:id \
        ORDER BY training_date DESC;"
    result = db.session.execute(sql, {"id":u_id})
    trainings = result.fetchall()
    return trainings

def get_loanedtools(u_id):
    """Return loaned tools"""
    sql = "SELECT loanedtools.loandate, tools.tool, tools.serialnumber \
        FROM tsohaproject.loanedtools LEFT JOIN tsohaproject.tools \
        ON (loanedtools.tool_id = tools.tool_id) \
        WHERE user_id = :id AND loanedtools.loaned = true;"
    result = db.session.execute(sql, {"id":u_id})
    tools = result.fetchall()
    return tools

def get_userinfo(u_id):
    """Return basic userinformation from table users"""
    # Get basic information TO-DO: REPLACE * WITH COLUMNS NEEDED!
    sql = "SELECT * FROM tsohaproject.users WHERE user_id =:id"
    result = db.session.execute(sql, {"id":u_id})
    user = result.fetchone()
    return user

def get_activityinformation(u_id):
    """Get activityinformation"""
    sql = "SELECT activitylevel.level, currentactivity.level_date \
        FROM tsohaproject.users LEFT JOIN tsohaproject.currentactivity \
        ON users.user_id = currentactivity.user_id \
        LEFT JOIN tsohaproject.activitylevel \
        ON currentactivity.activity_id = activitylevel.activity_id \
        WHERE users.user_id=:id \
        ORDER BY currentactivity.level_date DESC"
    result = db.session.execute(sql, {"id":u_id})
    activity = result.fetchall
    return activity

def get_currentactivity(u_id):
    """Return selected users activity"""
    sql = "SELECT currentactivity.user_id, currentactivity.level_date, activitylevel.level \
        FROM tsohaproject.currentactivity LEFT JOIN tsohaproject.activitylevel \
        ON (currentactivity.activity_id = activitylevel.activity_id) \
        WHERE user_id =:id \
        ORDER BY level_date DESC \
        LIMIT 1"
    result = db.session.execute(sql, {"id":u_id})
    currectactivity = result.fetchone()
    return currectactivity


@app.route("/auth/login", methods=["POST", "GET"])
def authlogin():
    """This method validates an login attempt"""
    error = False
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"{password=}")
        sql = "SELECT users.user_id, users.role, password.password \
            FROM tsohaproject.users INNER JOIN tsohaproject.password \
            ON users.user_id = password.user_id \
            WHERE users.username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        # print(user.password)
        # print(check_password_hash(user.password, password))
        if not user:
            error = True
        else:
            if check_password_hash(user.password, password):
                session["user_id"] = user.user_id
                session["role"] = user.role
            else:
                error = True
    if error:
        return render_template("login.html", show=True, error=True, \
            message="Username or password is incorrect. Please try again.")
    role = user_role()
    if role == 'admin' or role == 'coordinator':
        return redirect("/users")
    return redirect("/volunteer-view")

def get_user_id():
    """Return id of logged in user"""
    u_id = session.get("user_id", 0)
    # print(f"user-id: {id}")
    return u_id

def get_role():
    """Return role of logged in user"""
    role = session.get("role", 0)
    return role

def user_role():
    """Returns role of logged in user differently"""
    u_id = get_user_id()
    if u_id != 0:
        sql = "SELECT role FROM tsohaproject.users WHERE user_id =:id"
        result = db.session.execute(sql, {"id":u_id})
        return result.fetchone()[0]
    else:
        return u_id

@app.route("/logout")
def logout_and_redirect():
    """Logs signed in user out"""
    logout()
    return redirect("/")

def logout():
    """Deletes user sessions"""
    del session["user_id"]
    del session["role"]
    return

@app.route("/volunteer-view")
def volunteerview():
    """Render volunteer's view"""
    role = user_role()
    if role != 'volunteer':
        return error("notauthorized")
    u_id = get_user_id()
    # Get basic information TO-DO: REPLACE * WITH COLUMNS NEEDED!
    sql = "SELECT * FROM tsohaproject.users WHERE user_id =:id"
    result = db.session.execute(sql, {"id":u_id})
    user = result.fetchone()
    # Get volunteer's activities - volunteer can participate in activities they are qualified in
    sql2 = "SELECT tasks.task_id, tasks.task \
        FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification \
        ON users.user_id = volunteerqualification.user_id \
        LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id \
        WHERE users.user_id=:id"
    result2 = db.session.execute(sql2, {"id":u_id})
    activities = result2.fetchall()
    sql3 = "SELECT messages.activity_date, messages.content, tasks.task \
        FROM tsohaproject.messages LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE messages.volunteer_id=:id \
        ORDER BY messages.activity_date DESC"
    result3 = db.session.execute(sql3, {"id":u_id})
    messages = result3.fetchall()
    print(messages)
    if len(messages) == 0:
        nomessages = True
    else:
        nomessages = False
    print(nomessages)
    return render_template("volunteer-view.html", user=user, \
        activities=activities, messages=messages, nomessages=nomessages)

@app.route("/auth/createadmin", methods=["POST"])
def createadmin():
    """This method receives a new registration and coordinates/handles validation,"""
    """saving to database and possible errors."""
    username = request.form["username"]
    password = request.form["password1"]
    password2 = request.form["password2"]
    role = "admin"
    isactive = True
    #Password validation => Move to another module
    if len(password) < 8:
        return render_template("register.html", show=True, \
            message="Password must be atleast 8 characters long.")
    if password != password2:
        return render_template("register.html", show=True, \
            message="Passwords do not match, try again.")
    hash_value = generate_password_hash(password)
    print(f"{password=}")
    # print(f"Hashvalue: {hash_value}")
    #TO-DO: This is not a recommended way of using a try. Fix this.
    try:
        sqlusers = "INSERT INTO tsohaproject.users (username,role,isactive) \
            VALUES (:username, :role, :isactive) RETURNING user_id"
        result = db.session.execute(sqlusers, \
            {"username":username, "role":role, "isactive": isactive})
        user_id = result.fetchone()[0]
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) \
            VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        db.session.commit()
    except:
        return render_template("register.html", show=True, \
            message="Something bad has happened, but I do not specifically know what. Try again.")
    return render_template("login.html", show=True, error=False, \
        message="Registeration completed. Please login with your account.")

@app.route("/docs/aboutus")
def about_us():
    """Render About Us view"""
    u_id = get_user_id()
    print(id)
    logged = False
    if u_id != 0:
        logged = True
    return render_template("docs/aboutus.html", logged=logged)

@app.route("/docs/feedback")
def feedback():
    """Render feedback view"""
    u_id = get_user_id()
    print(id)
    logged = False
    if u_id != 0:
        logged = True
    return render_template("docs/feedback.html", logged=logged)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Handle feedback submissions and render thank you view"""
    content = request.form["content"]
    now = date.today()
    print(now)
    return render_template("/docs/thank-you.html")

@app.route("/view-activities")
def supervisor_view_activities():
    """View messages as supervisor"""
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    #TO-DO: ORDER BY is not yet doing what I want.
    #Perhaps the activity_date (date) doesn't work for sorting as intended?
    sql = "SELECT messages.msg_id, messages.activity_date, messages.send_date, \
        messages.content, tasks.task, users.username, users.role, users.lastname, users.firstname \
        FROM tsohaproject.users INNER JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        ORDER BY messages.thread_id DESC, messages.activity_date ASC"
    # sql = "SELECT users.lastname, users.firstname, messages.msg_id, \
    # messages.activity_date, messages.content, tasks.task \
    # FROM tsohaproject.users INNER JOIN tsohaproject.messages \
    # ON (users.user_id = messages.volunteer_id) \
    # LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) \
    # ORDER BY messages.activity_date DESC"
    result = db.session.execute(sql)
    messages = result.fetchall()
    print(messages)
    if len(messages) == 0:
        nomessages = True
    else:
        nomessages = False
    print(nomessages)
    return render_template("message-view.html", messages=messages, nomessages=nomessages)

@app.route("/reply-msg/<int:id>")
def reply_msg(u_id):
    """Render reply to a message view"""
    sql = "SELECT users.lastname, users.firstname, messages.msg_id, \
        messages.activity_date, messages.content, tasks.task_id \
        FROM tsohaproject.users INNER JOIN tsohaproject.messages \
        ON (users.user_id = messages.volunteer_id) \
        LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) \
        WHERE msg_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    message = result.fetchone()
    return render_template("reply-msg.html", id=u_id, message=message)

@app.route("/submit-reply/<int:id>", methods=["POST"])
def submit_reply(u_id):
    """Submit reply"""
    sql = "SELECT volunteer_id FROM tsohaproject.messages WHERE msg_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    volunteer_id = result.fetchone()[0]
    sender_id = get_user_id()
    thread_id = u_id
    task_id = request.form["task_id"]
    content = request.form["content"]
    msg_sent = datetime.now(timezone.utc)
    #TO-DO: This is not a recommended way of using a try. Fix this.
    try:
        sql = "INSERT INTO tsohaproject.messages \
            (thread_id, volunteer_id, sender_id, task_id, send_date, content) \
            VALUES (:thread_id, :volunteer_id, :sender_id, :task_id, :send_date, :content)"
        result = db.session.execute(sql, {"thread_id":thread_id, "volunteer_id":volunteer_id, \
            "sender_id":sender_id, "task_id":task_id, "send_date":msg_sent, "content":content})
        db.session.commit()
    except:
        return render_template("error.html", show=True, \
            error="Something bad has happened, \
                but at this demo-stage I do not exactly know what. Try again.")
    return redirect("/view-activities")

@app.route("/search-activities")
def supervisor_search_activities():
    """Search activities"""
    role = user_role()
    if not role == 'admin' or role == 'coordinator':
        return error("notauthorized")
    query = request.args["query"]
    sql = "SELECT messages.msg_id, messages.activity_date, messages.content, \
        tasks.task, users.username, users.role, users.lastname, users.firstname \
        FROM tsohaproject.users INNER JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE LOWER(messages.content) LIKE LOWER(:query) \
        ORDER BY messages.thread_id DESC, messages.activity_date ASC"
    # sql = "SELECT users.lastname, users.firstname, messages.msg_id, \
    # messages.activity_date, messages.content, tasks.task \
    # FROM tsohaproject.users INNER JOIN tsohaproject.messages \
    # ON (users.user_id = messages.volunteer_id) \
    # LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) \
    # WHERE messages.content LIKE :query ORDER BY messages.activity_date DESC"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    messages = result.fetchall()
    if len(messages) == 0:
        nomessages = True
    else:
        nomessages = False
    print(nomessages)
    return render_template("message-view.html", \
        messages=messages, nomessages=nomessages)

# TO-DO: CLEAN THIS AWAY
# @app.route("/send", methods=["POST"])
# def send():
#     content = request.form["content"]
#     sql = "INSERT INTO messages (content) VALUES (:content)"
#     db.session.execute(sql, {"content":content})
#     db.session.commit()
#     return redirect("/")
