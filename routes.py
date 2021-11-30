from app import app
from os import getenv
import os
import re
from datetime import datetime, date, timezone
from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
# from flask import session
from sqlalchemy.sql.elements import False_, Null
from werkzeug.security import check_password_hash, generate_password_hash
import users, hrqueries, messages

@app.route("/")
def index():
    """Render landing page"""
    return render_template("index.html")

@app.route("/login")
def login():
    """Render login page"""
    return render_template("login.html")

@app.route("/auth/login", methods=["POST", "GET"])
def authlogin():
    """This function routes an login attempt"""
    is_error = False
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            if users.is_coordinator():
                return redirect("/users")
        else: 
            return render_template("login.html", show=True, error=True, \
            message="Username or password is incorrect. Please try again.")
    return redirect("/volunteer-view")

@app.route("/register")
def register():
    """Render registration page"""
    return render_template("register.html", show=False)

@app.route("/logout")
def logout_and_redirect():
    """Logs signed in user out"""
    users.logout()
    return redirect("/")

@app.route("/auth/createadmin", methods=["POST"])
def createadmin():
    """Create an admin account for testing purposes."""
    username = request.form["username"]
    password = request.form["password1"]
    password2 = request.form["password2"]
    valid_password = users.password_valid(password, password2)
    if not valid_password[0]:
        render_template("register.html", show=True, \
            message=valid_password[1])
    hash_value = generate_password_hash(password)
    users.create_admin(username, hash_value)
    return render_template("login.html", show=True, error=False, \
        message="Registration completed. Please login with your account.")

#ADMIN/COORDINATOR ROUTES
@app.route("/users")
def view_users():
    """Check validation and fetch userinformation"""
    if not users.is_coordinator():
        return error("notauthorized")
    volunteer_info = hrqueries.volunteer_list()
    return render_template("users.html", count=len(volunteer_info), users=volunteer_info)

@app.route("/addnew", methods=["POST"])
def addnew():
    """TO-DO: CLEAN THIS AWAY"""
    return render_template("addnew.html")


#TO-DO: Function too long. This how to split.
@app.route("/submituser", methods=["POST"])
def submituser():
    """Check validation, add a new user"""
    if not users.is_coordinator():
        return error("notauthorized")
    if 'role' in request.form:
        role = request.form["role"]
    else:
        role = None
    qualifications = request.form.getlist("qualification")
    params = [request.form["lastname"], request.form["firstname"], \
        request.form["email"], request.form["startdate"], \
            role, request.form["username"]]
    # Check that all fields have information
    userinfo_is_valid = users.validate_userinfo(params, qualifications)
    if not userinfo_is_valid[0]:
        return render_template("addnew.html", \
            show=True, message=userinfo_is_valid[1], filled=params)
    #Password validation => TO-DO: Move to another module
    password = request.form["password"]
    password2 = request.form["password2"]
    valid_password = users.password_valid(password, password2)
    if not valid_password[0]:
        render_template("addnew.html", show=True, \
            message=valid_password[1], filled=params)
    hash_value = generate_password_hash(password)
    if not users.create_useraccount(params, qualifications, hash_value):
        return render_template("addnew.html", show=True, \
            message="An error has occured. This means that most likely the username was already taken."\
                    , filled=params)
    return redirect("/users")

@app.route("/update-user/<int:u_id>", methods=["POST"])
def update_user(u_id):
    """Old userinfo is fetched from database and updated for those fields that can be updated."""
    # Get basic information TO-DO: REPLACE * WITH COLUMNS NEEDED!
    oldinfo = hrqueries.get_userinfo(u_id)
    isactive = True
    if request.form.get("terminate") is not None:
        isactive = False
    if not isactive:
        enddate = date.today()
        print(enddate)
    else:
        enddate = None
    newinfo = [oldinfo[0], request.form["role"], request.form["lastname"], request.form["firstname"]\
        , request.form["username"], request.form["email"], request.form["phone"], \
        request.form["startdate"], enddate, oldinfo[9], isactive]
    if not hrqueries.update_userinfo(newinfo):
        return render_template("error.html", logged=True, error="Something bad has happened, \
            but at this demo-stage I do not exactly know what. Try again.")
    if not isactive:
        return redirect("/users")
    return redirect("/view-user/" + str(u_id))

@app.route("/view-user/<int:u_id>")
def viewuser(u_id):
    """Render singe user's informationpage"""
    if not users.is_coordinator():
        return error("notauthorized")
    user = hrqueries.get_userinfo(u_id)
    qualifications = hrqueries.get_qualifiations(u_id)
    currentactivity = hrqueries.get_currentactivity(u_id)
    trainings = hrqueries.get_additionaltrainings(u_id)
    tools = hrqueries.get_loanedtools(u_id)
    return render_template("view-user.html", user=user, qualifications=qualifications, \
        currentactivity=currentactivity, trainings=trainings, tools=tools)

# TO-DO - see why post? Shouldn't it be GET?
@app.route("/edit-user/<int:u_id>", methods=["GET", "POST"])
def edituser(u_id):
    """Render edit-user page"""
    if not users.is_coordinator():
        return error("notauthorized")
    if request.method == "POST":
        user = hrqueries.get_userinfo(u_id)
        qualifications = hrqueries.get_qualifiations(u_id)
        activity = hrqueries.get_activityinformation(u_id)
        return render_template("edit-user.html", user=user, \
            qualifications=qualifications, activity=activity)
    # If method is GET - render basic template
    return render_template("edit-user.html")

@app.route("/view-activities")
def supervisor_view_activities():
    """View messages as supervisor"""
    if not users.is_coordinator():
        return error("notauthorized")
    #TO-DO: ORDER BY is not yet doing what I want.
    #Perhaps the activity_date (date) doesn't work for sorting as intended?
    all_messages = messages.fetch_all_messages()
    no_messages = bool(len(all_messages) == 0)
    return render_template("message-view.html", messages=all_messages, nomessages=no_messages)

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
    sender_id = users.get_user_id()
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
    role = users.user_role()
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
    nomessages = bool(len(messages) == 0)
    # if len(messages) == 0:
    #     nomessages = True
    # else:
    #     nomessages = False
    print(nomessages)
    return render_template("message-view.html", \
        messages=messages, nomessages=nomessages)


#VOLUNTEER ROUTES
@app.route("/volunteer-view")
def volunteerview():
    """Render volunteer's view"""
    if not users.is_volunteer():
        return error("notauthorized")
    u_id = users.get_user_id()
    user = hrqueries.get_userinfo(u_id)
    activities = hrqueries.get_activities(u_id)
    volunteer_messages = messages.fetch_volunteer_messages(u_id)
    nomessages = bool(len(volunteer_messages) == 0)
    return render_template("volunteer-view.html", user=user, \
        activities=activities, messages=volunteer_messages, nomessages=nomessages)

@app.route("/submit-message-volunteer/<int:u_id>", methods=["POST"])
def submit_message_volunteer(u_id):
    """This function stores a new message."""
    if not users.is_volunteer():
        return error("notauthorized")
    message = {"activity_date":request.form["date"], \
        "sender_id":u_id, \
        "volunteer_id":u_id, \
        "task_id":int(request.form["doneactivity"]), \
        "content": request.form["content"], \
        "msg_sent":datetime.now(timezone.utc)}
    messages.new_message(message)
    return redirect("/volunteer-view")

#INFORMATIONROUTES
@app.route("/docs/aboutus")
def about_us():
    """Render About Us view"""
    u_id = users.get_user_id()
    print(id)
    logged = False
    if u_id != 0:
        logged = True
    return render_template("docs/aboutus.html", logged=logged)

@app.route("/docs/feedback")
def feedback():
    """Render feedback view"""
    u_id = users.get_user_id()
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
    print(now, content)
    return render_template("/docs/thank-you.html")

def error(description):
    """Render Error view"""
    u_id = users.get_user_id()
    logged = False
    if u_id != 0:
        logged = True
    if description == 'notauthorized':
        message = ('You have tried to access a page that you are not authorized to view. \
            Please make sure you are logged in. If the problem continues, \
                please leave feedback on the issue. Feedback form can be found in the footer.')
    return render_template("error.html", error=message, logged=logged)



# TO-DO: CLEAN THIS AWAY
# @app.route("/send", methods=["POST"])
# def send():
#     content = request.form["content"]
#     sql = "INSERT INTO messages (content) VALUES (:content)"
#     db.session.execute(sql, {"content":content})
#     db.session.commit()
#     return redirect("/")


# @app.route("/new")
# def new():
#     """TO-DO: CLEAN THIS AWAY"""
#     return render_template("new.html")