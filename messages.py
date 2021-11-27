from db import db



def fetch_all_messages():
    """Fetch and return messages"""
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
    return result.fetchall()

def fetch_volunteer_messages(u_id):
    sql = "SELECT messages.activity_date, messages.content, tasks.task \
        FROM tsohaproject.messages LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE messages.volunteer_id=:id \
        ORDER BY messages.activity_date DESC"
    result = db.session.execute(sql, {"id":u_id})
    return result.fetchall()

def new_message(message: dict):
    """Submit new message"""
    sql = "INSERT INTO tsohaproject.messages (volunteer_id, sender_id, task_id, activity_date, \
        send_date, content) \
        VALUES (:volunteer_id, :sender_id, :task_id, :activity_date, :send_date, :content) \
        RETURNING msg_id"
    result = db.session.execute(sql, {"volunteer_id":message["volunteer_id"], "sender_id":message["sender_id"], \
        "task_id":message["task_id"], "activity_date":message["activity_date"], "send_date":message["msg_sent"], \
        "content":message["content"]})
    msg_id = result.fetchone()[0]
    sql_update = "UPDATE tsohaproject.messages SET thread_id=:msg_id WHERE msg_id=:msg_id"
    db.session.execute(sql_update, {"msg_id":msg_id})
    db.session.commit()
    #TO-DO: Remove if not needed
    # except:
    #     return render_template("volunteer-view", show=True, message="Something bad has happened, \
    #         but at this demo-stage I do not exactly know what. Try again.")