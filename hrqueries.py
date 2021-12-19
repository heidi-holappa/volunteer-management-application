from db import db

def update_userinfo(newinfo: dict):
    """Updates user information"""
    sql = "UPDATE tsohaproject.users \
        SET role=:role, lastname=:lastname, firstname=:firstname, username=:username, \
            email=:email, phone=:phone, startdate=:startdate, enddate=:enddate, \
            basictraining=:basictraning, isactive=:isactive \
        WHERE user_id=:user_id"
    db.session.execute(sql, {"role":newinfo["role"], "lastname":newinfo["lastname"],
        "firstname":newinfo["firstname"], "username":newinfo["username"], "email":newinfo["email"],
        "phone":newinfo["phone"], "startdate":newinfo["startdate"], "enddate":newinfo["enddate"],
        "basictraning":newinfo["basictraining"], "isactive":newinfo["isactive"],
        "user_id":newinfo["user_id"]})
    db.session.commit()


def add_qualifications(qualifications: list, user_id: int):
    """Adds qualifications to a user"""
    for task_id in qualifications:
        if task_id != "":
            sql = "INSERT INTO tsohaproject.volunteerqualification (task_id, user_id) \
                    VALUES (:task_id, :user_id)"
            db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
    db.session.commit()

def get_active_user_list(role: str):
    """Returns active users with specified role"""
    sql = "SELECT users.user_id, users.role, users.lastname, \
        users.firstname, users.username, users.email, users.phone, \
        startdate, COUNT(messages.sender_id) AS activitycounter \
    FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
    ON (users.user_id = messages.sender_id) \
    WHERE role=:role AND isactive='true' \
    GROUP BY users.user_id \
    ORDER BY users.lastname ASC"
    result = db.session.execute(sql, {"role":role})
    return result.fetchall()

def submit_account_edit(newinfo: list):
    """Updates user account"""
    sql = "UPDATE tsohaproject.users SET \
        lastname=:lastname, \
        firstname=:firstname, \
        email=:email, \
        phone=:phone \
        WHERE user_id=:user_id"
    db.session.execute(sql, {"user_id":newinfo[0], "lastname":newinfo[1],
            "firstname":newinfo[2], "email":newinfo[3], "phone":newinfo[4]})
    db.session.commit()

def search_userlist(u_query: str, role: str):
    """ Return searched string from columns firstname, lastname, email"""
    sql = "SELECT users.user_id, users.role, users.lastname, users.firstname, \
        users.username, users.email, users.phone, startdate, \
        COUNT(messages.sender_id) AS activitycounter, user_id, \
        lastname || ' ' || firstname || ' ' || email AS document  \
        FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) \
        WHERE role=:role AND isactive='true' \
        AND LOWER(lastname || ' ' || firstname || ' ' || email) LIKE LOWER(:query) \
        GROUP BY users.user_id;"
    result = db.session.execute(sql, {"query":'%' + u_query + '%', "role":role})
    return result.fetchall()

def get_report_data():
    """This method returns some simple report data"""
    result = {}
    msg_and_thread_count  = "SELECT COUNT(DISTINCT(thread_id)), COUNT(*) \
        FROM tsohaproject.messages"
    msg_count = db.session.execute(msg_and_thread_count)
    result["messages"] = msg_count.fetchall()
    user_count = "SELECT role,  COUNT(*) FROM tsohaproject.users \
        WHERE users.isactive = 'True' GROUP BY role ORDER BY role ASC"
    user_count_result = db.session.execute(user_count)
    result["active_users"] = user_count_result.fetchall()
    loans_sql = "SELECT COUNT(*), \
        (SELECT COUNT(*) FROM tsohaproject.loanedtools WHERE loaned='True') \
        FROM tsohaproject.loanedtools "
    loans = db.session.execute(loans_sql)
    result["loans"] = loans.fetchall()
    equipment_sql = "SELECT COUNT(*), \
        (SELECT COUNT(*) FROM tsohaproject.tools WHERE active='True') \
        FROM tsohaproject.tools"
    equipment = db.session.execute(equipment_sql)
    result["equipment"] = equipment.fetchall()
    trainings_sql = "SELECT COUNT(*), \
        (SELECT COUNT(*) FROM tsohaproject.additionaltrainings WHERE active='True') \
        FROM tsohaproject.additionaltrainings"
    loans_by_type_sql = "SELECT tool, COUNT(user_id) as C \
        FROM tsohaproject.tools LEFT JOIN \
        tsohaproject.loanedtools ON \
        (tools.tool_id = loanedtools.tool_id) \
        GROUP BY tool \
        ORDER BY c DESC"
    loans_by_type = db.session.execute(loans_by_type_sql)
    result["loans_by_type"] = loans_by_type.fetchall()
    trainings = db.session.execute(trainings_sql)
    result["trainings"] = trainings.fetchall()
    training_participation_sql = "SELECT training, COUNT(user_id) AS c \
        FROM tsohaproject.additionaltrainings \
        LEFT JOIN tsohaproject.trainingparticipation \
        ON (additionaltrainings.training_id = \
        trainingparticipation.training_id) \
        GROUP BY training \
        ORDER BY c DESC"
    training_participation = db.session.execute(training_participation_sql)
    result["training_participation"] = training_participation.fetchall()
    active_loans_sql = "SELECT tools.tool, COUNT(tools.tool), \
        COALESCE(SUM(CASE WHEN loanedtools.loaned='True' THEN 1 ELSE 0 END)) \
        FROM tsohaproject.tools LEFT JOIN tsohaproject.loanedtools \
        ON (tools.tool_id = loanedtools.tool_id) \
        GROUP BY tool \
        ORDER BY tool ASC"
    active_loans = db.session.execute(active_loans_sql)
    result["active_loans"] = active_loans.fetchall()
    return result

def get_qualifiations(u_id):
    """Return qualifications"""
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
    return qualifications

def get_additionaltrainings(u_id):
    """Return taken trainings for selected user"""
    sql = "SELECT additionaltrainings.training, trainingparticipation.training_date \
        FROM tsohaproject.trainingparticipation LEFT JOIN tsohaproject.additionaltrainings \
        ON (trainingparticipation.training_id = additionaltrainings.training_id) \
        WHERE user_id =:id \
        ORDER BY training_date DESC;"
    result = db.session.execute(sql, {"id":u_id})
    trainings = result.fetchall()
    return trainings

def get_current_trainings():
    """Return all submitted training options"""
    sql = "SELECT training_id, training, description, active \
        FROM tsohaproject.additionaltrainings \
        ORDER BY active DESC"
    result = db.session.execute(sql)
    return result

def add_new_training_module(training: str, description: str):
    """Add a new training module"""
    sql = "INSERT INTO tsohaproject.additionaltrainings (training, description, active) \
        VALUES (:training, :description, 'True')"
    db.session.execute(sql, {"training":training, "description":description})
    db.session.commit()

def training_set_activity(active, t_id):
    """Change training activity state to true or false"""
    sql = "UPDATE tsohaproject.additionaltrainings SET active = :active WHERE training_id = :t_id"
    db.session.execute(sql, {"active":active, "t_id":t_id})
    db.session.commit()

def get_possible_trainings():
    """Get all active trainings"""
    sql = "SELECT training_id, training \
        FROM tsohaproject.additionaltrainings \
        WHERE active='True'"
    result = db.session.execute(sql)
    return result

def get_available_tools():
    """get all active tools"""
    sql = "SELECT tool_id, tool \
        FROM tsohaproject.tools \
        WHERE loaned='FALSE' AND active='True'"
    result = db.session.execute(sql)
    return result

def get_all_tools():
    """Get all submitted tools"""
    sql = "SELECT tool_id, tool, serialnumber, loaned, active \
        FROM tsohaproject.tools \
        ORDER BY active DESC"
    return db.session.execute(sql)

def add_new_tool(tool: list):
    """Add new tool"""
    sql = "INSERT INTO tsohaproject.tools (tool, serialnumber, loaned, active) \
        VALUES (:tool, :serialnumber, 'False', 'True')"
    db.session.execute(sql, {"tool":tool[0], "serialnumber":tool[1]})
    db.session.commit()

def tool_set_activity(active, t_id):
    """Set tool active state to true or false"""
    sql = "UPDATE tsohaproject.tools SET active = :active WHERE tool_id = :t_id"
    db.session.execute(sql, {"active":active, "t_id":t_id})
    db.session.commit()

def add_loan(loaned_tool):
    """Add loan to database"""
    sql_a = "INSERT INTO tsohaproject.loanedtools (user_id, tool_id, loandate, loaned) \
        VALUES (:user_id, :tool_id, :loandate, 'TRUE')"
    db.session.execute(sql_a, {"user_id":loaned_tool[1], "tool_id":loaned_tool[0],
        "loandate":loaned_tool[2]})
    sql_b = "UPDATE tsohaproject.tools SET loaned='TRUE' WHERE tool_id=:id"
    db.session.execute(sql_b, {"id":loaned_tool[0]})
    db.session.commit()

def get_loanedtools(u_id):
    """Return loaned tools"""
    sql = "SELECT tools.tool_id, loanedtools.loandate, tools.tool, tools.serialnumber \
        FROM tsohaproject.loanedtools LEFT JOIN tsohaproject.tools \
        ON (loanedtools.tool_id = tools.tool_id) \
        WHERE user_id = :id AND loanedtools.loaned = true;"
    result = db.session.execute(sql, {"id":u_id})
    tools = result.fetchall()
    return tools

def get_userinfo(u_id):
    """Return extensive userinformation from table users"""
    sql = "SELECT user_id, role, lastname, firstname, username, email, \
        phone, startdate, basictraining, isactive FROM tsohaproject.users WHERE user_id =:id"
    result = db.session.execute(sql, {"id":u_id})
    user = result.fetchone()
    return user

def get_activities(u_id):
    """Get available activities for a selected user"""
    sql = "SELECT tasks.task_id, tasks.task \
        FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification \
        ON users.user_id = volunteerqualification.user_id \
        LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id \
        WHERE users.user_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    return result.fetchall()

def get_current_activity_level(u_id):
    """Get activityinformation"""
    sql = "SELECT currentactivity.activity_id AS a_id, activitylevel.level AS level, \
        currentactivity.level_date AS a_date \
        FROM tsohaproject.users LEFT JOIN tsohaproject.currentactivity \
        ON users.user_id = currentactivity.user_id \
        LEFT JOIN tsohaproject.activitylevel \
        ON currentactivity.activity_id = activitylevel.activity_id \
        WHERE currentactivity.user_id=:id \
        ORDER BY a_date DESC \
        LIMIT 1"
    result = db.session.execute(sql, {"id":u_id})
    activity = result.fetchone()
    return activity

def update_activity_level(a_date, u_id, a_id):
    """Update user's activitylevel"""
    sql = "INSERT INTO tsohaproject.currentactivity (level_date, user_id, activity_id) \
        VALUES (:a_date, :u_id, :a_id)"
    db.session.execute(sql, {"a_date":a_date, "u_id":u_id, "a_id":a_id})
    db.session.commit()

def loan_return(tool_id):
    """Return a loaned tool"""
    sql_a = "UPDATE tsohaproject.tools SET loaned='FALSE' WHERE tool_id=:id"
    sql_b = "UPDATE tsohaproject.loanedtools SET loaned='FALSE' \
        WHERE tool_id=:id AND loaned='TRUE' RETURNING user_id"
    db.session.execute(sql_a, {"id":tool_id})
    result = db.session.execute(sql_b, {"id":tool_id})
    db.session.commit()
    user_id = result.fetchone()[0]
    return user_id

def add_training_participation(training_info: list):
    """Add training participation to a selected volunteed"""
    sql = "INSERT INTO tsohaproject.trainingparticipation \
        (training_id, user_id, training_date) \
            VALUES (:training_id, :user_id, :training_date)"
    db.session.execute(sql, {"training_id":training_info[0],
    "user_id":training_info[1], "training_date":training_info[2]})
    db.session.commit()

def log_mark(log: list):
    """Create a log action"""
    sql = "INSERT INTO tsohaproject.applog (user_id, timestamp, description) \
        VALUES (:user_id, :timestamp, :description)"
    db.session.execute(sql, {"user_id":log[0], "timestamp":log[1], "description":log[2]})
    db.session.commit()

def account_updated(newinfo: list):
    """Review whether account information has changed"""
    sql = "SELECT user_id, lastname, firstname, email, phone \
        FROM tsohaproject.users \
        WHERE user_id=:u_id"
    result = db.session.execute(sql, {"u_id":newinfo[0]})
    oldinfo = result.fetchone()
    updated = False
    for index, item in enumerate(newinfo):
        if newinfo[index] != oldinfo[index]:
            updated = True
    return updated

def get_all_loaned_tools():
    """Return all loaned tools"""
    sql = "SELECT tools.tool, tools.tool_id, users.firstname, users.lastname, \
        loanedtools.loandate \
        FROM tsohaproject.tools LEFT JOIN tsohaproject.loanedtools \
        ON tools.tool_id=loanedtools.tool_id \
        LEFT JOIN tsohaproject.users \
        ON loanedtools.user_id=users.user_id \
        WHERE loanedtools.loaned='True'"
    result = db.session.execute(sql)
    return result.fetchall()
