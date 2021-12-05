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
                return redirect("/view-volunteers")
        else: 
            return render_template("login.html", show=True, error=True, \
            message="Username or password is incorrect. Please try again.")
    return redirect("/volunteer-view/0")

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
    if len(username) < 3:
        return render_template("register.html", show=True, \
            message="Username must have atleast 3 characters")
    valid_password = users.password_valid(password, password2)
    if not valid_password[0]:
        return render_template("register.html", show=True, \
            message=valid_password[1])
    hash_value = generate_password_hash(password)
    if not users.create_admin(username, hash_value):
        return render_template("register.html", show=True, \
            message="Something went wrong. Most likely the username was already taken. Try again.")
    return render_template("login.html", show=True, error=False, \
        message="Registration completed. Please login with your account.")

#ADMIN/COORDINATOR ROUTES
@app.route("/view-volunteers")
def view_volunteers():
    """Check validation and fetch userinformation"""
    if not users.is_coordinator():
        return error("notauthorized")
    volunteer_info = hrqueries.get_active_user_list('volunteer')
    return render_template("users.html", count=len(volunteer_info), users=volunteer_info,
        volunteer_view = True, role=users.get_role())

@app.route("/view-coordinators")
def view_coordinators():
    """Check validation and fetch userinformation"""
    if not users.is_admin():
        return error("notauthorized")
    coordinator_info = hrqueries.get_active_user_list('coordinator')
    return render_template("users.html", count=len(coordinator_info), users=coordinator_info,
        volunteer_view = False, role=users.get_role())

@app.route("/search-volunteers")
def search_volunteers():
    """Search volunteers by firstname, lastname, email"""
    if not users.is_coordinator():
        return error("notauthorized")
    query = request.args["query"]
    content = hrqueries.search_userlist(query, 'volunteer')
    nousers = bool(len(content) == 0)
    print(nousers)
    return render_template("users.html", \
        users=content, count=len(content) ,nousers=nousers, role=users.get_role(),
        volunteer_view = True)

@app.route("/search-coordinators")
def search_coordinators():
    """Search coordinators by firstname, lastname, email"""
    if not users.is_admin():
        return error("notauthorized")
    query = request.args["query"]
    content = hrqueries.search_userlist(query, 'coordinator')
    nousers = bool(len(content) == 0)
    print(nousers)
    return render_template("users.html", \
        users=content, count=len(content) ,nousers=nousers, role=users.get_role())


# @app.route("/search-result")
# def search_volunteers():
#     """Search volunteers"""
#     if not users.is_coordinator():
#         return error("notauthorized")
#     volunteer_info = hrqueries.search_volunteerlist("s")
#     return render_template("users.html", count=len(volunteer_info), users=volunteer_info)

  

@app.route("/reporting", methods=["GET"])
def reporting():
    if not users.is_admin():
        return error("notauthorized")
    report_data = hrqueries.get_report_data()
    print(report_data)
    return render_template("reporting.html", role=users.get_role(),
    data = report_data)

@app.route("/add-user", methods=["POST", "GET"])
def submituser():
    """Check validation, add a new user"""
    if not users.is_coordinator():
        return error("notauthorized")
    if request.method == "GET":
        return render_template("add-user.html", user_role=users.get_role())
    if request.method == "POST":
        if 'role' in request.form:
            role = request.form["role"]
        else:
            role = None
        qualifications = list(request.form.getlist("qualification"))
        params = [request.form["lastname"], request.form["firstname"], \
            request.form["email"], request.form["startdate"], \
                role, request.form["username"]]
        # Check that all fields have information
        userinfo_is_valid = users.validate_userinfo(params, qualifications)
        if not userinfo_is_valid[0]:
            return render_template("addnew.html", \
                show=True, message=userinfo_is_valid[1], filled=params, role=users.get_role())
        #Password validation => TO-DO: Move to another module
        password = request.form["password"]
        password2 = request.form["password2"]
        valid_password = users.password_valid(password, password2)
        if not valid_password[0]:
            render_template("add-user.html", show=True, \
                message=valid_password[1], filled=params)
        hash_value = generate_password_hash(password)
        if not users.create_useraccount(params, qualifications, hash_value):
            return render_template("add-user.html", show=True, \
                message="An error has occured. This means that most likely the username was already taken."\
                        , filled=params, role=users.get_role())
        return redirect("/view-volunteers")

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
        request.form["startdate"], enddate, oldinfo[8], isactive]
    if 'qualification' in request.values:
        qualifications = request.form.getlist("qualification")
        hrqueries.add_qualifications(qualifications, newinfo[0])
    if not hrqueries.update_userinfo(newinfo):
        return render_template("error.html", logged=True, error="Something bad has happened, \
            but at this demo-stage I do not exactly know what. Try again.", 
            role=users.get_role())
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
    view='view-volunteers'
    return render_template("view-user.html", user=user, qualifications=qualifications, 
        currentactivity=currentactivity, trainings=trainings, tools=tools, view=view, 
        role=users.get_role())

@app.route("/view-account")
def view_account():
    """Render logged in user's informationpage"""
    u_id = users.get_user_id()
    if u_id == 0:
        return error("notauthorized")
    user = hrqueries.get_userinfo(u_id)
    qualifications = hrqueries.get_qualifiations(u_id)
    currentactivity = hrqueries.get_currentactivity(u_id)
    trainings = hrqueries.get_additionaltrainings(u_id)
    tools = hrqueries.get_loanedtools(u_id)
    return render_template("user-account.html", user=user, qualifications=qualifications, 
        currentactivity=currentactivity, trainings=trainings, tools=tools, 
        role=users.get_role())

@app.route("/edit-account")
def edit_account():
    """Render page for editing basic personal information"""
    u_id = users.get_user_id()
    if u_id == 0:
        return error("notauthorized")
    user = hrqueries.get_userinfo(u_id)
    return render_template("edit-account.html", user=user, 
        role=users.get_role())

@app.route("/submit-edit-account", methods=["POST"])
def submit_edit_account():
    """Save changes to account"""
    u_id = users.get_user_id()
    if u_id == 0:
        return error("notauthorized")
    newinfo = [u_id, request.form["lastname"], request.form["firstname"],
            request.form["email"], request.form["phone"]]
    hrqueries.submit_account_edit(newinfo)
    return redirect("/view-account")

@app.route("/return-loan/<int:tool_id>", methods=["POST"])
def return_loan(tool_id: int):
    user_id = hrqueries.loan_return(tool_id)
    return redirect("../view-user/" + str(user_id))

@app.route("/add-training/<int:u_id>", methods=["GET", "POST"])
def add_training(u_id):
    if not users.is_coordinator():
        return error("notauthorized")
    if request.method == "GET":
        user = hrqueries.get_userinfo(u_id)
        trainings = hrqueries.get_possible_trainings()
        return render_template("add-training.html", user=user, \
            trainings=trainings, role=users.get_role())
    if request.method == "POST":
        if not ('training_id' in request.form and 'date' in request.form):
            return error("missing_value")
        training_id = request.form["training_id"]
        participation_date = request.form["date"]
        if len(training_id) == 0 or len(participation_date) == 0:
            return error("missing_value")
        training = [training_id, u_id, participation_date]
        hrqueries.add_training_participation(training)
        return redirect("../view-user/" + str(u_id))

@app.route("/add-loan/<int:u_id>", methods=["GET", "POST"])
def add_loaned_tool(u_id):
    if request.method == "GET":
        user = hrqueries.get_userinfo(u_id)
        tools = hrqueries.get_available_tools()
        return render_template("add-loan.html", user=user, \
            tools=tools, role=users.get_role())
    if request.method == "POST":
        loaned_tool = [request.form["tool_id"], u_id, request.form["date"]]
        hrqueries.add_loan(loaned_tool)
        return redirect("../view-user/" + str(u_id))

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
            qualifications=qualifications, activity=activity, role=users.get_role())
    return render_template("edit-user.html", role=users.get_role())


@app.route("/view-activities/<int:set_offset>")
def supervisor_view_activities(set_offset):
    """View messages as supervisor"""
    if not users.is_coordinator():
        return error("notauthorized")
    #TO-DO: ORDER BY is not yet doing what I want.
    #Perhaps the activity_date (date) doesn't work for sorting as intended?
    limit = 5
    offset = set_offset * 5
    if 'query' in request.args and len(request.args["query"]) != 0:
        query = request.args["query"]
        active_query = True
    else:
        query = ""
        active_query = False
    fetched_messages = messages.fetch_all_messages(limit,offset, query)
    print(fetched_messages)
    count_messages = messages.fetch_message_count(query)
    show_next = bool(count_messages > limit * (set_offset+1))
    show_previous = bool(set_offset > 0)
    no_messages = bool(len(fetched_messages) == 0)
    return render_template("message-view.html", messages=fetched_messages, \
        nomessages=no_messages, show_next=show_next, show_previous=show_previous, \
            offset=set_offset, msg_count=count_messages, active_query=active_query, \
                query=query, role=users.get_role())

@app.route("/reply-msg/<int:m_id>")
def reply_msg(m_id):
    """Render reply to a message view"""
    message = messages.fetch_selected_message(m_id)
    return render_template("reply-msg.html", id=m_id, message=message, 
        role=users.get_role())

@app.route("/submit-reply/<int:u_id>", methods=["POST"])
def submit_reply(u_id):
    """Submit reply"""
    volunteer_id = messages.get_op_id(u_id)
    sender_id = users.get_user_id()
    thread_id = u_id
    task_id = request.form["task_id"]
    content = request.form["content"]
    msg_sent = datetime.now(timezone.utc)
    msg_sent_date = date.today()
    new_reply = [thread_id, volunteer_id, sender_id, task_id, msg_sent, content, msg_sent_date]    
    #TO-DO: This is not a recommended way of using a try. Fix this.
    messages.submit_reply(new_reply)
    return redirect("/view-activities/0")

@app.route("/add-training-module", methods=["GET", "POST"])
def add_new_training():
    if request.method == "GET":
        current_trainings = hrqueries.get_current_trainings()
        return render_template("add-training-module.html", trainings=current_trainings, show=False, \
            message="", error=False, role=users.get_role())
    if request.method == "POST":
        if not ('training' in request.form and 'description' in request.form):
            error("missing_values")
        new_training = request.form["training"]
        description = request.form["description"]
        if len(new_training) == 0 or len(description) == 0:
            session["error"] = True
            return redirect("/training-submission")
        hrqueries.add_new_training_module(new_training, description)
        session["error"] = False
        return redirect("/training-submission")
        
@app.route("/training-submission")
def training_submission_handling():
    current_trainings = hrqueries.get_current_trainings()
    error = session.get("error", 0)
    if error:
        return render_template("add-training-module.html", \
                message="Please fill in all fields.", error=True, show=True, \
                    trainings=current_trainings, role=users.get_role())
    return render_template("add-training-module.html", show=True, error=False, \
            message="New module successfully added.", trainings=current_trainings, 
            role=users.get_role())


@app.route("/training-active/<int:isactive>/<int:t_id>")
def training_active(isactive: int, t_id: int):
    active = bool(isactive == 1)
    hrqueries.training_set_activity(active, t_id)
    return redirect("/add-training-module")

@app.route("/add-tool", methods=["POST", "GET"])
def add_new_tool():
    if request.method == "GET":
        tools = hrqueries.get_all_tools()
        return render_template("add-tool.html", show=False, tools=tools, role=users.get_role())
    if request.method == "POST":
        if len(request.form["tool"]) == 0 or len(request.form["serialnumber"])== 0:
            session["error"] = True
            return redirect("/tool-submission")
        hrqueries.add_new_tool([request.form["tool"], request.form["serialnumber"]])
        session["error"] = False
        return redirect("/tool-submission")

@app.route("/tool-active/<int:isactive>/<int:t_id>")
def tool_active(isactive: int, t_id: int):
    active = bool(isactive == 1)
    hrqueries.tool_set_activity(active, t_id)
    return redirect("/add-tool")

@app.route("/tool-submission")
def tool_submission():
    tools = hrqueries.get_all_tools()
    error = session.get("error", 0)
    if error:
        return render_template("add-tool.html", tools=tools, show=True, \
            error=True, message="Please fill in both fields to submit a new tool.", 
            role=users.get_role())
    return render_template("add-tool.html", tools=tools, show=True, \
            error=False, message="New tool added successfully.", 
            role=users.get_role())



# @app.route("/search-activities")
# def supervisor_search_activities():
#     """Search activities"""
#     role = users.user_role()
#     if not role == 'admin' or role == 'coordinator':
#         return error("notauthorized")
#     query = request.args["query"]
#     content = messages.search_messages(query)
#     nomessages = bool(len(content) == 0)
#     # if len(messages) == 0:
#     #     nomessages = True
#     # else:
#     #     nomessages = False
#     print(nomessages)
#     return render_template("message-view.html", \
#         messages=content, nomessages=nomessages)



#VOLUNTEER ROUTES
@app.route("/volunteer-view/<int:set_offset>")
def volunteerview(set_offset):
    """Render volunteer's view"""
    if not users.is_volunteer():
        return error("notauthorized")
    limit=5
    offset = set_offset * limit
    u_id = users.get_user_id()
    user = hrqueries.get_userinfo(u_id)
    activities = hrqueries.get_activities(u_id)
    volunteer_messages = messages.fetch_volunteer_messages(u_id, limit, offset)
    count_messages = len(volunteer_messages)
    show_next = bool(count_messages > limit * (set_offset+1))
    show_previous = bool(set_offset > 0)
    nomessages = bool(len(volunteer_messages) == 0)
    return render_template("volunteer-view.html", user=user, \
        activities=activities, messages=volunteer_messages, nomessages=nomessages, \
            show_previous=show_previous, show_next=show_next, 
            role=users.get_role())

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
    return redirect("/volunteer-view/0")

#INFORMATIONROUTES
@app.route("/success")
def success():
    return render_template("success.html", role=users.get_role())

@app.route("/docs/aboutus")
def about_us():
    """Render About Us view"""
    u_id = users.get_user_id()
    logged = bool(u_id != 0)
    role = users.get_role()
    return render_template("docs/aboutus.html", logged=logged, role=role)

@app.route("/docs/feedback")
def feedback():
    """Render feedback view"""
    u_id = users.get_user_id()
    logged = bool(u_id != 0)
    role = users.get_role()
    return render_template("docs/feedback.html", logged=logged, role=role)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Handle feedback submissions and render thank you view"""
    content = request.form["content"]
    fb_date = date.today()
    messages.submit_feedback(fb_date, content)
    return render_template("/docs/thank-you.html", role=users.get_role())

def error(description):
    """Render Error view"""
    u_id = users.get_user_id()
    logged = bool(u_id != 0)
    role = users.get_role()
    message = "This is a general error message. Something caused an error, but there is not \
        enough information to tell what. Feedback on the error would be appreciated! \
            We apologize for the inconvenience."
    if description == 'notauthorized':
        message = 'You have tried to access a page that you are not authorized to view. \
            Please make sure you are logged in. If the problem continues, \
                please leave feedback on the issue. Feedback form can be found in the footer.'
    if description == 'missing_value':
        message = 'One or more fields were left empty. Please fill in all fields carefully.'
    return render_template("error.html", error=message, logged=logged, role=role)



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

