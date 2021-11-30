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
    sql = "SELECT users.user_id, users.role, users.lastname, users.firstname, users.username, users.email, users.phone, startdate, COUNT(messages.sender_id) AS activitycounter \
    FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
    ON (users.user_id = messages.sender_id) \
    WHERE role='volunteer' AND isactive='true' \
    GROUP BY users.user_id;"
    result = db.session.execute(sql)
    return result.fetchall()

def get_limited_volunteerinfo(u_id):
    """Return limited userinformation on  active users from table users"""
    sql = "SELECT user_id, role, lastname, firstname, username, email FROM tsohaproject.users WHERE isactive = TRUE"
    result = db.session.execute(sql, {"id":u_id})
    user = result.fetchone()
    return user


def get_active_volunteerinfo(u_id):
    """Return active userinformation from table users"""
    sql = "SELECT user_id, role, lastname, firstname, username, email, phone, startdate, basictraining FROM tsohaproject.users WHERE isactive = TRUE"
    result = db.session.execute(sql, {"id":u_id})
    user = result.fetchone()
    return user



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

