# import re
from app import app
from datetime import datetime, date, timezone
# from flask import Flask
from flask import flash, redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash
import users, hrqueries, messages, error_handlers

@app.route("/")
def index():
    """Render landing page"""
    if users.get_user_id() != 0:
        users.logout()
    return render_template("index.html")

@app.route("/login")
def login():
    """Render login page"""
    if users.get_user_id() != 0:
        return redirect("/logout")
    return render_template("login.html")

@app.route("/auth/login", methods=["POST", "GET"])
def authlogin():
    """This function routes an login attempt"""
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            error_handlers.log_action("Action: login")
            flash("You have logged in successfully.", "success")
            if users.is_coordinator():
                return redirect("/view-volunteers")
        else: 
            flash("Username or password is incorrect. Please try again.", "danger")
            return render_template("login.html")
    return redirect("/volunteer-view/0")

@app.route("/register")
def register():
    """Render registration page"""
    return render_template("register.html", show=False)

@app.route("/logout")
def logout_and_redirect():
    """Logs signed in user out"""
    users.logout()
    flash("You have been successfully logged out.", "success")
    return redirect("/")

@app.route("/auth/createadmin", methods=["POST"])
def createadmin():
    """Create an admin account for testing purposes."""
    username = request.form["username"]
    password = request.form["password1"]
    password2 = request.form["password2"]
    errors = False
    if len(username) < 3:
        error_handlers.log_action("Creating an admin account failed. Username too short.")
        flash("Username must have atleast 3 characters", "danger")
        errors = True
    valid_password = users.password_valid(password, password2)
    if not valid_password:
        error_handlers.log_action("Creating an admin account failed. Password too short.")
        flash("Password too short. Password must have atleast 8 characters", "danger")
        errors = True
    if errors:
        return redirect("/register")
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
        abort(403)
    rply_requests = messages.check_reply_requests()
    volunteer_info = hrqueries.get_active_user_list("volunteer")
    return render_template("users.html", count=len(volunteer_info), users=volunteer_info,
        volunteer_view = True, rply_requests=rply_requests)

@app.route("/view-coordinators")
def view_coordinators():
    """Check validation and fetch userinformation"""
    if not users.is_admin():
        abort(403)
    rply_requests = messages.check_reply_requests()
    coordinator_info = hrqueries.get_active_user_list("coordinator")
    return render_template("users.html", count=len(coordinator_info), users=coordinator_info,
        volunteer_view = False, rply_requests=rply_requests)

@app.route("/search-volunteers")
def search_volunteers():
    """Search volunteers by firstname, lastname, email"""
    if not users.is_coordinator():
        abort(403)
    rply_requests = messages.check_reply_requests()
    query = request.args["query"]
    content = hrqueries.search_userlist(query, "volunteer")
    nousers = bool(len(content) == 0)
    return render_template("users.html", \
        users=content, count=len(content) ,nousers=nousers, volunteer_view = True, \
            rply_requests=rply_requests)

@app.route("/search-coordinators")
def search_coordinators():
    """Search coordinators by firstname, lastname, email"""
    if not users.is_admin():
        abort(403)
    rply_requests = messages.check_reply_requests()
    query = request.args["query"]
    content = hrqueries.search_userlist(query, "coordinator")
    nousers = bool(len(content) == 0)
    return render_template("users.html", \
        users=content, count=len(content) ,nousers=nousers, rply_requests=rply_requests)

@app.route("/reporting", methods=["GET"])
def reporting():
    if not users.is_admin():
        abort(403)
    report_data = hrqueries.get_report_data()
    rply_requests = messages.check_reply_requests()
    return render_template("reporting.html", data = report_data, rply_requests=rply_requests)

@app.route("/add-user", methods=["POST", "GET"])
def submituser():
    """Check validation, add a new user"""
    if not users.is_coordinator():
        abort(403)
    if request.method == "GET":
        rply_requests = messages.check_reply_requests()
        return render_template("add-user.html", rply_requests=rply_requests)
    if request.method == "POST":            
        if "role" in request.form:
            role = request.form["role"]
        else:
            role = None
        qualifications = list(request.form.getlist("qualification"))
        time_stamp = datetime.now(timezone.utc)
        # If time change this into a dictionary
        params = [request.form["lastname"], request.form["firstname"], \
            request.form["email"], request.form["startdate"], \
                role, request.form["username"], time_stamp ]
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        # Check that all fields have information
        userinfo_is_valid = users.validate_userinfo(params, qualifications)
        if not userinfo_is_valid:
            flash("Please fill in all required user info and choose at least one qualification", "danger")
            return render_template("add-user.html", filled=params, show=True)
        password = request.form["password"]
        password2 = request.form["password2"]
        valid_password = users.password_valid(password, password2)
        if not valid_password:
            flash("Password not valid. Please make sure the password has atleast 8 characters and that passwords match.", "danger")
            render_template("add-user.html", filled=params, show=True)
        hash_value = generate_password_hash(password)
        if not users.create_useraccount(params, qualifications, hash_value):
            flash("An error has occured. This means that most likely the username \
                was already taken.", "danger")
            return render_template("add-user.html", filled=params, show=True)
        flash("User created successfully.", "success")
        return redirect("/view-volunteers")

@app.route("/update-user/<int:u_id>", methods=["POST"])
def update_user(u_id):
    """Old userinfo is fetched from database and updated for those fields that can be updated."""
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    
    isactive = bool(request.form.get("terminate") is None)
    if not isactive:
        enddate = date.today()
    else:
        enddate = None
    
    # IF TIME CHANGE TO DICTIONARY
    oldinfo = hrqueries.get_userinfo(u_id)
    newinfo = {"user_id": oldinfo[0],
                "role": request.form["role"],
                "lastname": request.form["lastname"],
                "firstname": request.form["firstname"],
                "username": request.form["username"],
                "email": request.form["email"],
                "phone": request.form["phone"],
                "startdate": request.form["startdate"],
                "enddate": enddate, 
                "basictraining": oldinfo[8],
                "isactive": isactive}
    
    if len(newinfo["username"]) == 0 or len(newinfo["lastname"]) == 0 or len(newinfo["firstname"]) == 0:
        flash("Update failed. Following fields can not be empty: username, lastname, firstname", "danger")
        return redirect("/edit-user/" + str(u_id))

    hrqueries.update_userinfo(newinfo)

    if "qualification" in request.values:
        qualifications = request.form.getlist("qualification")
        hrqueries.add_qualifications(qualifications, newinfo["user_id"])
    
    
    
    if users.is_volunteer_with_id(u_id):
        a_id = request.form["activity"]
        if int(a_id) != int(hrqueries.get_current_activity_level(u_id)[0]):
            hrqueries.update_activity_level(datetime.now(timezone.utc), u_id, a_id)

    if not isactive:
        flash("Account terminated successfully", "success")
        if newinfo["role"] == "volunteer":
            return redirect("../view-volunteers")
        return redirect("../view-coordinators")
    
    flash("User information submitted successfully. Possible changes saved.", "success")
    if len(newinfo["phone"]) == 0 or len(newinfo["email"]) == 0 or len(newinfo["startdate"]) == 0:
        flash("Note: one of the fields Phone, Email or Startdate were left empty. \
            It is adviced to fill in these fields.", "info")
    return redirect("/view-user/" + str(u_id))

@app.route("/view-user/<int:u_id>")
def viewuser(u_id):
    """Render singe user"s informationpage"""
    if not users.is_coordinator():
        abort(403)
    rply_requests = messages.check_reply_requests()
    user = hrqueries.get_userinfo(u_id)
    qualifications = hrqueries.get_qualifiations(u_id)
    currentactivity = hrqueries.get_current_activity_level(u_id)
    trainings = hrqueries.get_additionaltrainings(u_id)
    tools = hrqueries.get_loanedtools(u_id)
    if user[1] == "volunteer":
        view="view-volunteers"
    else:
        view="view-coordinators"
    return render_template("view-user.html", user=user, qualifications=qualifications, 
        currentactivity=currentactivity, trainings=trainings, tools=tools, view=view, \
        rply_requests=rply_requests)

@app.route("/view-account")
def view_account():
    """Render logged in user"s informationpage"""
    u_id = users.get_user_id()
    if u_id == 0:
        abort(403)
    user = hrqueries.get_userinfo(u_id)
    rply_requests = messages.check_reply_requests()
    qualifications = hrqueries.get_qualifiations(u_id)
    currentactivity = hrqueries.get_current_activity_level(u_id)
    trainings = hrqueries.get_additionaltrainings(u_id)
    tools = hrqueries.get_loanedtools(u_id)
    return render_template("user-account.html", user=user, qualifications=qualifications, 
        currentactivity=currentactivity, trainings=trainings, tools=tools, rply_requests=rply_requests)

@app.route("/edit-account")
def edit_account():
    """Render page for editing basic personal information"""
    rply_requests = messages.check_reply_requests()
    u_id = users.get_user_id()
    if u_id == 0:
        abort(403)
    user = hrqueries.get_userinfo(u_id)
    return render_template("edit-account.html", user=user, rply_requests=rply_requests)

@app.route("/submit-edit-account", methods=["POST"])
def submit_edit_account():
    """Save changes to account"""
    u_id = users.get_user_id()
    if u_id == 0 or session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    old_password = request.form["password0"]
    new_password = request.form["password1"]
    retype_new_password = request.form["password2"]
    change_password = bool(len(old_password) != 0) or bool(len(new_password) != 0) or bool(len(retype_new_password) != 0)
    newinfo = [u_id, request.form["lastname"], request.form["firstname"],
            request.form["email"], request.form["phone"]]
    if hrqueries.account_updated(newinfo):
        hrqueries.submit_account_edit(newinfo)
        flash("Personal information updated successfully.", "success")
    else:
        flash("Nothing was changed, no updates made", "info")
    if change_password:
        pw_updated = users.update_password(old_password, new_password, retype_new_password)
        if pw_updated:
            flash("Password changed successfully", "success")
        else:
            flash("Password update failed. \
                Please make sure you filled in all fields and that the old password is correct. \
                New password must containt 8 characters.", "danger")
    return redirect("/edit-account")

@app.route("/return-loan/<int:tool_id>", methods=["POST"])
def return_loan(tool_id: int):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    user_id = hrqueries.loan_return(tool_id)
    if request.form["page"] == 'loaned-tools':
        return redirect("../loaned-tools")
    return redirect("../view-user/" + str(user_id))

@app.route("/add-training/<int:u_id>", methods=["GET", "POST"])
def add_training(u_id):
    if not users.is_coordinator():
        abort(403)
    if request.method == "GET":
        user = hrqueries.get_userinfo(u_id)
        trainings = hrqueries.get_possible_trainings()
        rply_requests = messages.check_reply_requests()
        return render_template("add-training.html", user=user, \
            trainings=trainings, rply_requests=rply_requests)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if not ("training_id" in request.form and len(request.form["date"]) != 0):
            flash("Please fill in all fields carefully.", "danger")
            return redirect("/add-training/" + str(u_id))
        training_id = request.form["training_id"]
        participation_date = request.form["date"]
        if len(training_id) == 0 or len(participation_date) == 0:
            flash("Please fill in all fields carefully.", "danger")
            return redirect("/add-training/" + str(u_id))
        training = [training_id, u_id, participation_date]
        hrqueries.add_training_participation(training)
        flash("Training added successfully", "success")
        return redirect("../view-user/" + str(u_id))

@app.route("/add-loan/<int:u_id>", methods=["GET", "POST"])
def add_loaned_tool(u_id):
    if request.method == "GET":
        user = hrqueries.get_userinfo(u_id)
        tools = hrqueries.get_available_tools()
        rply_requests = messages.check_reply_requests()
        return render_template("add-loan.html", user=user, 
            tools=tools, rply_requests=rply_requests)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if not ("tool_id" in request.form and len(request.form["date"]) != 0):
            flash("Please fill in all fields carefully.", "danger")
            return redirect("/add-loan/" + str(u_id))
        loaned_tool = [request.form["tool_id"], u_id, request.form["date"]]
        hrqueries.add_loan(loaned_tool)
        flash("Loan added successfully", "success")
        return redirect("../view-user/" + str(u_id))

@app.route("/edit-user/<int:u_id>", methods=["GET", "POST"])
def edituser(u_id):
    """Render edit-user page"""
    if not users.is_coordinator():
        abort(403)
    if request.method == "GET":
        user = hrqueries.get_userinfo(u_id)
        qualifications = hrqueries.get_qualifiations(u_id)
        activity = hrqueries.get_current_activity_level(u_id)
        rply_requests = messages.check_reply_requests()
        return render_template("edit-user.html", user=user, 
            qualifications=qualifications, activity=activity)
    rply_requests = messages.check_reply_requests()
    return render_template("edit-user.html", rply_requests=rply_requests)

@app.route("/view-activities/<int:set_offset>", methods=["GET","POST"])
def supervisor_view_activities(set_offset):
    """View reported activities as a supervisor"""
    
    if not users.is_coordinator():
        abort(403)
    
    # Check if user wants to filter messages by volunteer name

    if "sender" in request.args: 
        sender = request.args["sender"]
        if sender != "showall":
            u_id = int(sender)
            filter=u_id
            filter_msg = f"Showing messages for {users.get_name(u_id)}"
        else:
            filter = "showall"
            filter_msg = ""
    else:
        filter = "showall"
        filter_msg = ""
    
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if "sender" in request.form:
            if request.form["sender"] == "showall":
                filter = "showall"
            else:
                u_id = int(request.form["sender"])
                filter=u_id
                filter_msg = f"Showing messages for {users.get_name(u_id)}"            
    
    limit = 5
    offset = set_offset * 5
    
    request_filter = False
    if "query" in request.args and len(request.args["query"]) != 0:
        query = request.args["query"]
        active_query = True
    else:
        query = ""
        active_query = False

    if "request-filter-on" in request.form:
        fetched_messages = messages.fetch_reply_request_messages(limit, offset)
        count_messages = len(fetched_messages)
        request_filter = True
    elif filter == "showall":
        fetch_thread_ids = messages.fetch_thread_ids(limit, offset, query)
        thread_ids = tuple(value[0] for value in fetch_thread_ids)
        count_messages = messages.fetch_thread_count(query)
        if len(thread_ids) != 0:
            fetched_messages = messages.fetch_paginated_threads(thread_ids)
        else:
            fetched_messages = []
    else: 
        fetch_thread_ids = messages.fetch_volunteer_threads(u_id, limit, offset, query)
        thread_ids = tuple(value[0] for value in fetch_thread_ids)
        fetched_messages = messages.fetch_volunteer_thread_msgs(thread_ids)
        count_messages = messages.fetch_volunteer_thread_count(u_id, query)
    
    fetch_message_senders = messages.fetch_message_senders()
    
    show_next = bool(count_messages > limit * (set_offset+1))
    show_previous = bool(set_offset > 0)
    no_messages = bool(len(fetched_messages) == 0)
    
    rply_requests = messages.check_reply_requests()
    return render_template("message-view.html", messages=fetched_messages, 
        nomessages=no_messages, show_next=show_next, show_previous=show_previous, 
            offset=set_offset, msg_count=count_messages, active_query=active_query, 
                query=query, users=fetch_message_senders, 
                show=filter, show_msg=filter_msg, rply_requests=rply_requests, request_filter=request_filter)

@app.route("/reply-msg/<int:m_id>")
def reply_msg(m_id):
    """Render reply to a message view"""
    message = messages.fetch_selected_message(m_id)
    rply_requests = messages.check_reply_requests()
    return render_template("reply-msg.html", id=m_id, message=message, \
        rply_requests=rply_requests)

@app.route("/submit-reply/<int:m_id>", methods=["POST"])
def submit_reply(m_id):
    """Submit reply"""
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    if len(request.form["content"]) < 10:
        flash("Content length must be atleast 10 characters", "error")
        return redirect("/reply-msg/" + str(m_id))
    volunteer_id = messages.get_op_id(m_id)
    sender_id = users.get_user_id()
    thread_id = m_id
    if messages.get_reply_requested(m_id):
        messages.remove_reply_request(m_id)
    task_id = request.form["task_id"]
    content = request.form["content"]
    msg_sent = datetime.now(timezone.utc)
    msg_sent_date = messages.get_op_date(m_id)
    new_reply = [thread_id, volunteer_id, sender_id, task_id, msg_sent, content, msg_sent_date]    
    messages.submit_reply(new_reply)
    flash("Reply posted successfully", "success")
    return redirect("/view-activities/0")

@app.route("/add-training-module", methods=["GET", "POST"])
def add_new_training():
    if request.method == "GET":
        current_trainings = hrqueries.get_current_trainings()
        rply_requests = messages.check_reply_requests()
        return render_template("add-training-module.html", trainings=current_trainings, show=False, 
            message="", error=False, rply_requests=rply_requests)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if not ("training" in request.form and "description" in request.form):
            flash("Please fill in all fields carefully", "danger")
        new_training = request.form["training"]
        description = request.form["description"]
        if len(new_training) == 0 or len(description) == 0:
            flash("Please fill in all fields carefully", "danger")
            return redirect("/training-submission")
        hrqueries.add_new_training_module(new_training, description)
        flash("Training added succesfully", "success")
        return redirect("/training-submission")
        
@app.route("/training-submission")
def training_submission_handling():
    current_trainings = hrqueries.get_current_trainings()
    rply_requests = messages.check_reply_requests()
    return render_template("add-training-module.html", trainings=current_trainings, \
            rply_requests=rply_requests)

@app.route("/training-active/<int:isactive>/<int:t_id>")
def training_active(isactive: int, t_id: int):
    active = bool(isactive == 1)
    hrqueries.training_set_activity(active, t_id)
    return redirect("/add-training-module")

@app.route("/add-tool", methods=["POST", "GET"])
def add_new_tool():
    if request.method == "GET":
        tools = hrqueries.get_all_tools()
        rply_requests = messages.check_reply_requests()
        return render_template("add-tool.html", show=False, tools=tools, \
            rply_requests=rply_requests)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if len(request.form["tool"]) == 0 or len(request.form["serialnumber"])== 0:
            flash("Please carefully fill in all fields.", "danger")
            return redirect("/tool-submission")
        hrqueries.add_new_tool([request.form["tool"], request.form["serialnumber"]])
        flash("New tool added successfully.", "success")
        return redirect("/tool-submission")

@app.route("/tool-active/<int:isactive>/<int:t_id>")
def tool_active(isactive: int, t_id: int):
    active = bool(isactive == 1)
    hrqueries.tool_set_activity(active, t_id)
    return redirect("/add-tool")

@app.route("/tool-submission")
def tool_submission():
    tools = hrqueries.get_all_tools()
    error = session.get("danger", 0)
    rply_requests = messages.check_reply_requests()
    if error:
        return render_template("add-tool.html", tools=tools, show=True, 
            error=True, message="Please fill in both fields to submit a new tool.", \
                rply_requests=rply_requests)
    return render_template("add-tool.html", tools=tools, show=True, 
            error=False, message="New tool added successfully.", rply_requests=rply_requests)

@app.route("/loaned-tools")
def loaned_tools():
    loaned_tools = hrqueries.get_all_loaned_tools()
    return render_template("loaned-tools.html", loaned_tools=loaned_tools)
    


#VOLUNTEER ROUTES
@app.route("/volunteer-view/<int:set_offset>")
def volunteerview(set_offset):
    """Render volunteer"s view"""
    if not users.is_volunteer():
        abort(403)
    error_msg=""
    success_msg=""
    if session.get("success"):
        session["success"]=False
        success_msg="Message submitted"
    limit=5
    query = ""
    offset = set_offset * limit
    u_id = users.get_user_id()
    user = hrqueries.get_userinfo(u_id)
    activities = hrqueries.get_activities(u_id)
    threads = messages.fetch_volunteer_threads(u_id, limit, offset, query)  
    thread_ids = tuple(value[0] for value in threads)
    if len(thread_ids) != 0:
        volunteer_messages = messages.fetch_volunteer_thread_msgs(thread_ids)
    else:
        volunteer_messages = []
    count_messages = messages.fetch_message_count_by_user(u_id)
    show_next = bool(count_messages > limit * (set_offset+1))
    show_previous = bool(set_offset > 0)
    nomessages = bool(len(volunteer_messages) == 0)
    return render_template("volunteer-view.html", user=user, 
        activities=activities, messages=volunteer_messages, nomessages=nomessages, 
            show_previous=show_previous, show_next=show_next, offset=set_offset,
            error_msg=error_msg, success_msg=success_msg)

@app.route("/submit-message-volunteer/<int:u_id>", methods=["POST"])
def submit_message_volunteer(u_id):
    """This function stores a new message."""
    if session["csrf_token"] != request.form["csrf_token"] or not users.is_volunteer():
            abort(403)
    if len(request.form["date"]) == 0 or len(request.form["doneactivity"]) == 0 \
        or len(request.form["content"]) < 10 or len(request.form["title"]) == 0:
        flash("Please fill in carefully all fields." "danger")
        return redirect("/volunteer-view/0")
    message = {"activity_date":request.form["date"], 
        "sender_id":u_id, 
        "volunteer_id":u_id, 
        "task_id":int(request.form["doneactivity"]), 
        "title": request.form["title"],
        "content": request.form["content"], 
        "msg_sent":datetime.now(timezone.utc), 
        "reply_request": bool("request-reply" in request.form)}
    messages.new_message(message)
    flash("Message submitted successfully.", "success")
    return redirect("/volunteer-view/0")
