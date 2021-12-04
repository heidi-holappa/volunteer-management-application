from db import db



def fetch_all_messages(limit: int, offset: int, query: str):
    """Fetch and return messages"""
    sql = "SELECT messages.msg_id, messages.activity_date, messages.send_date, \
        messages.content, tasks.task, users.username, users.role, users.lastname, users.firstname \
        FROM tsohaproject.users INNER JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE LOWER(messages.content) LIKE LOWER(:query) \
        ORDER BY messages.activity_date DESC, messages.thread_id DESC, messages.activity_date ASC \
        LIMIT :limit OFFSET :offset"
    # sql = "SELECT users.lastname, users.firstname, messages.msg_id, \
    # messages.activity_date, messages.content, tasks.task \
    # FROM tsohaproject.users INNER JOIN tsohaproject.messages \
    # ON (users.user_id = messages.volunteer_id) \
    # LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) \
    # ORDER BY messages.activity_date DESC"
    result = db.session.execute(sql, {"limit":limit, "offset":offset, "query":"%"+query+"%"})
    return result.fetchall()

def fetch_message_count(query):
    sql = "SELECT COUNT(*) FROM tsohaproject.messages \
        WHERE LOWER(messages.content) LIKE LOWER(:query)"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    count = result.fetchone()[0]
    print(f"Count of messages: {count}")
    return count


def fetch_volunteer_messages(u_id: int, limit: int, offset: int):
    sql = "SELECT users.username, users.lastname, users.firstname, users.role, \
        messages.activity_date, messages.content, tasks.task \
        FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
        ON users.user_id = messages.sender_id \
        LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE messages.volunteer_id=:id \
        ORDER BY messages.activity_date DESC, messages.thread_id DESC, messages.msg_id ASC \
        LIMIT :limit OFFSET :offset"
    result = db.session.execute(sql, {"id":u_id, "limit":limit, "offset":offset})
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

def search_messages(query: str):
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
    return result.fetchall()

def fetch_selected_message(m_id):
    """Fetches a selected message from the database"""
    sql = "SELECT users.lastname, users.firstname, messages.msg_id, \
        messages.activity_date, messages.content, tasks.task_id \
        FROM tsohaproject.users INNER JOIN tsohaproject.messages \
        ON (users.user_id = messages.volunteer_id) \
        LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) \
        WHERE msg_id=:id"
    result = db.session.execute(sql, {"id":m_id})
    return result.fetchone()

def fetch_feedback():
    """Fetches all received feedback"""
    sql = "SELECT feedback_date, content \
        FROM tsohaproject.feeback"
    result = db.session.execute(sql)
    return result.fetchall()

def submit_feedback(fb_date, content):
    """Stores a feedback to the database"""
    sql = "INSERT INTO tsohaproject.feedback (feedback_date, content) \
        VALUES (:fb_date, :content)"
    db.session.execute(sql, {"fb_date":fb_date, "content":content})
    db.session.commit()

def get_op_id(u_id):
    sql = "SELECT volunteer_id FROM tsohaproject.messages WHERE msg_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    return result.fetchone()[0]

def submit_reply(new_reply: list):
    sql = "INSERT INTO tsohaproject.messages \
            (thread_id, volunteer_id, sender_id, task_id, send_date, content) \
            VALUES (:thread_id, :volunteer_id, :sender_id, :task_id, :send_date, :content)"
    result = db.session.execute(sql, {"thread_id":new_reply[0], "volunteer_id":new_reply[1], \
            "sender_id":new_reply[2], "task_id":new_reply[4], "send_date":new_reply[5], "content":new_reply[6]})
    db.session.commit()