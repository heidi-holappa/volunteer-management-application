from sqlalchemy.util.langhelpers import _SQLA_RE
from db import db

def update_userinfo(newinfo: list):
    try:
        sql = "UPDATE tsohaproject.users \
            SET role=:role, lastname=:lastname, firstname=:firstname, username=:username, email=:email, \
                phone=:phone, startdate=:startdate, enddate=:enddate, basictraining=:basictraning, isactive=:isactive \
            WHERE user_id=:user_id"
        db.session.execute(sql, {"role":newinfo[1], "lastname":newinfo[2], "firstname":newinfo[3], \
            "username":newinfo[4], "email":newinfo[5], "phone":newinfo[6], "startdate":newinfo[7], \
            "enddate":newinfo[8], "basictraning":newinfo[9], "isactive":newinfo[10], \
            "user_id":newinfo[0]})
        db.session.commit()
        return True
    except:
        return False

def volunteer_list():
    sql = "SELECT users.user_id, users.role, users.lastname, \
        users.firstname, users.username, users.email, users.phone, \
        startdate, COUNT(messages.sender_id) AS activitycounter \
    FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
    ON (users.user_id = messages.sender_id) \
    WHERE role='volunteer' AND isactive='true' \
    GROUP BY users.user_id;"
    result = db.session.execute(sql)
    return result.fetchall()

def search_volunteerlist(u_query: str):
    """ Return searched string from columns firstname, lastname, email"""
    # sql = "SELECT users.user_id, users.role, users.lastname, \
    #     users.firstname, users.username, users.email, \
    #     users.phone, startdate, COUNT(messages.sender_id) AS activitycounter \
    #     FROM (SELECT user_id, lastname || ' ' || firstname || ' ' || email \
    #     AS document FROM tsohaproject.users WHERE role='volunteer') as subset \
    #     LEFT JOIN tsohaproject.users ON (subset.user_id = users.user_id) \
    #     LEFT JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) \
    #     WHERE role='volunteer' AND isactive='true' \
    #     AND LOWER(document) LIKE LOWER(:query) \
    #     GROUP BY users.user_id"
    sql = "SELECT users.user_id, users.role, users.lastname, users.firstname, \
        users.username, users.email, users.phone, startdate, \
        COUNT(messages.sender_id) AS activitycounter, user_id, \
        lastname || ' ' || firstname || ' ' || email AS document  \
        FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) \
        WHERE role='volunteer' AND isactive='true' \
        AND (lastname || ' ' || firstname || ' ' || email) LIKE :query \
        GROUP BY users.user_id;"
    result = db.session.execute(sql, {"query":'%' + u_query + '%'})
    return result.fetchall()


def get_limited_volunteerinfo():
    """Return limited userinformation on  active users from table users"""
    sql = "SELECT user_id, role, lastname, firstname, username, email \
        FROM tsohaproject.users WHERE isactive = TRUE"
    result = db.session.execute(sql)
    return result.fetchall()

def get_active_volunteerinfo():
    """Return active userinformation from table users"""
    sql = "SELECT user_id, role, lastname, firstname, username, \
        email, phone, startdate, basictraining \
        FROM tsohaproject.users WHERE isactive = TRUE"
    result = db.session.execute(sql)
    return result.fetchall()

def get_current_trainings():
    """Return training options"""
    sql = "SELECT training FROM tsohaproject.additionaltrainings"
    result = db.session.execute(sql)
    return result

def add_new_training_module(training: str):
    sql = "INSERT INTO tsohaproject.additionaltrainings (training) VALUES (:training)"
    db.session.execute(sql, {"training":training})
    db.session.commit()


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

def get_possible_trainings():
    sql = "SELECT training_id, training \
        FROM tsohaproject.additionaltrainings"
    result = db.session.execute(sql)
    return result

def get_available_tools():
    sql = "SELECT tool_id, tool \
        FROM tsohaproject.tools \
        WHERE loaned='FALSE'"
    result = db.session.execute(sql)
    return result

def get_all_tools():
    sql = "SELECT tool, serialnumber, loaned \
        FROM tsohaproject.tools"
    return db.session.execute(sql)

def add_new_tool(tool: list):
    sql = "INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES (:tool, :serialnumber, 'False')"
    db.session.execute(sql, {"tool":tool[0], "serialnumber":tool[1]})
    db.session.commit()

def add_loan(loaned_tool):
    sql_a = "INSERT INTO tsohaproject.loanedtools (user_id, tool_id, loandate, loaned) VALUES (:user_id, :tool_id, :loandate, 'TRUE')"
    db.session.execute(sql_a, {"user_id":loaned_tool[1], "tool_id":loaned_tool[0], "loandate":loaned_tool[2]})
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
    sql = "SELECT user_id, role, lastname, firstname, username, email, phone, startdate, basictraining, isactive FROM tsohaproject.users WHERE user_id =:id"
    result = db.session.execute(sql, {"id":u_id})
    user = result.fetchone()
    return user

def get_activities(u_id):
    sql = "SELECT tasks.task_id, tasks.task \
        FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification \
        ON users.user_id = volunteerqualification.user_id \
        LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id \
        WHERE users.user_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    return result.fetchall()

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

def loan_return(tool_id):
    sql_a = "UPDATE tsohaproject.tools SET loaned='FALSE' WHERE tool_id=:id"
    sql_b = "UPDATE tsohaproject.loanedtools SET loaned='FALSE' WHERE tool_id=:id AND loaned='TRUE' RETURNING user_id"
    db.session.execute(sql_a, {"id":tool_id})
    result = db.session.execute(sql_b, {"id":tool_id})
    db.session.commit()
    user_id = result.fetchone()[0]
    return user_id

def add_training_participation(training_info: list):
    sql = "INSERT INTO tsohaproject.trainingparticipation (training_id, user_id, training_date) VALUES (:training_id, :user_id, :training_date)"
    db.session.execute(sql, {"training_id":training_info[0], "user_id":training_info[1], "training_date":training_info[2]})
    db.session.commit()
    return

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

