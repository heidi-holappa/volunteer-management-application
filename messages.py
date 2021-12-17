from db import db

def fetch_all_messages(limit: int, offset: int, query: str):
    """Fetch and return messages"""
    if len(query) == 0:
        sql = "SELECT messages.msg_id, messages.activity_date, messages.send_date, \
            messages.title, messages.content, messages.reply_request, tasks.task, \
            users.username, users.role, users.lastname, users.firstname \
            FROM tsohaproject.users INNER JOIN tsohaproject.messages \
            ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
            ON (messages.task_id = tasks.task_id) \
            WHERE LOWER(messages.content) LIKE LOWER(:query) \
            ORDER BY activity_date DESC, thread_id, msg_id ASC \
            LIMIT :limit OFFSET :offset"
    else:
        sql = "SELECT messages.msg_id, messages.activity_date, messages.send_date, \
            messages.title, messages.content, messages.reply_request, tasks.task, \
            users.username, users.role, users.lastname, users.firstname \
            FROM tsohaproject.users INNER JOIN tsohaproject.messages \
            ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
            ON (messages.task_id = tasks.task_id) \
            WHERE LOWER(messages.content) LIKE LOWER(:query) AND volunteer_id = sender_id \
            ORDER BY activity_date DESC, thread_id, msg_id ASC \
            LIMIT :limit OFFSET :offset"
    result = db.session.execute(sql, {"limit":limit, "offset":offset, "query":"%"+query+"%"})
    return result.fetchall()

def fetch_reply_request_messages(limit: int, offset: int, query: str):
    """Fetch and return messages"""
    if len(query) == 0:
        sql = "SELECT messages.msg_id, messages.activity_date, messages.send_date, \
            messages.title, messages.content, messages.reply_request, tasks.task, \
            users.username, users.role, users.lastname, users.firstname \
            FROM tsohaproject.users INNER JOIN tsohaproject.messages \
            ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
            ON (messages.task_id = tasks.task_id) \
            WHERE LOWER(messages.content) LIKE LOWER(:query) AND reply_request='True' \
            ORDER BY reply_request DESC, activity_date DESC, thread_id, msg_id ASC \
            LIMIT :limit OFFSET :offset"
    else:
        sql = "SELECT messages.msg_id, messages.activity_date, messages.send_date, \
            messages.title, messages.content, messages.reply_request, tasks.task, \
            users.username, users.role, users.lastname, users.firstname \
            FROM tsohaproject.users INNER JOIN tsohaproject.messages \
            ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
            ON (messages.task_id = tasks.task_id) \
            WHERE LOWER(messages.content) LIKE LOWER(:query) AND volunteer_id = sender_id \
            AND AND reply_request='True' \
            ORDER BY reply_request DESC, activity_date DESC, thread_id, msg_id ASC \
            LIMIT :limit OFFSET :offset"
    result = db.session.execute(sql, {"limit":limit, "offset":offset, "query":"%"+query+"%"})
    return result.fetchall()

def fetch_message_count(query):
    sql = "SELECT COUNT(*) FROM tsohaproject.messages \
        WHERE LOWER(messages.content) LIKE LOWER(:query)"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    count = result.fetchone()[0]
    return count

def fetch_volunteer_message_count(u_id, query):
    sql = "SELECT COUNT(*) FROM tsohaproject.messages \
        WHERE LOWER(messages.content) LIKE LOWER(:query) \
        AND volunteer_id=:id"
    result = db.session.execute(sql, {"query":"%"+query+"%", "id":u_id})
    count = result.fetchone()[0]
    return count

def fetch_message_count_by_user(u_id):
    sql = "SELECT COUNT(*) FROM tsohaproject.messages \
        WHERE messages.volunteer_id=:u_id"
    result = db.session.execute(sql, {"u_id":u_id})
    return result.fetchone()[0]

def fetch_volunteer_messages(u_id: int, limit: int, offset: int, query: str):
    sql = "SELECT users.username, users.lastname, users.firstname, users.role, \
        messages.activity_date, messages.title, messages.content, tasks.task, \
        messages.reply_request, messages.msg_id, messages.send_date \
        FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
        ON users.user_id = messages.sender_id \
        LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE messages.volunteer_id=:id AND LOWER(messages.content) LIKE LOWER(:query)\
        ORDER BY reply_request DESC, activity_date DESC, thread_id, msg_id ASC \
        LIMIT :limit OFFSET :offset"
    result = db.session.execute(sql, {"id":u_id, "limit":limit, "offset":offset, \
        "query":"%"+query+"%"})
    return result.fetchall()

def new_message(message: dict):
    """Submit new message"""
    sql = "INSERT INTO tsohaproject.messages (volunteer_id, sender_id, task_id, activity_date, \
        send_date, title, content, reply_request) \
        VALUES (:volunteer_id, :sender_id, :task_id, :activity_date, :send_date, :title, \
            :content, :reply_request) \
        RETURNING msg_id"
    result = db.session.execute(sql, {"volunteer_id":message["volunteer_id"], "sender_id":message["sender_id"], \
        "task_id":message["task_id"], "activity_date":message["activity_date"], "send_date":message["msg_sent"], \
        "title":message["title"] ,"content":message["content"], "reply_request":message["reply_request"]})
    msg_id = result.fetchone()[0]
    sql_update = "UPDATE tsohaproject.messages SET thread_id=:msg_id WHERE msg_id=:msg_id"
    db.session.execute(sql_update, {"msg_id":msg_id})
    db.session.commit()

def search_messages(query: str):
    sql = "SELECT messages.msg_id, messages.activity_date, messages.title, messages.content, \
        messages.reply_request, tasks.task, users.username, users.role, users.lastname, users.firstname \
        FROM tsohaproject.users INNER JOIN tsohaproject.messages \
        ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks \
        ON (messages.task_id = tasks.task_id) \
        WHERE LOWER(messages.content) LIKE LOWER(:query) \
        ORDER BY messages.thread_id DESC, messages.activity_date ASC"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    return result.fetchall()

def fetch_selected_message(m_id):
    """Fetches a selected message from the database"""
    sql = "SELECT users.lastname, users.firstname, messages.msg_id, \
        messages.activity_date, messages.title, messages.content, messages.reply_request, \
        tasks.task_id \
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

def submit_reply(new_reply: list):
    sql = "INSERT INTO tsohaproject.messages \
            (thread_id, volunteer_id, sender_id, task_id, send_date, content, activity_date, reply_request) \
            VALUES (:thread_id, :volunteer_id, :sender_id, :task_id, \
            :send_date, :content, :activity_date, 'False')"
    db.session.execute(sql, {"thread_id":new_reply[0], "volunteer_id":new_reply[1], \
            "sender_id":new_reply[2], "task_id":new_reply[3], "send_date":new_reply[4], 
            "content":new_reply[5], "activity_date":new_reply[6]})
    db.session.commit()

def get_op_id(u_id):
    """ Returns the volunteer_id of the selected message"""
    sql = "SELECT volunteer_id FROM tsohaproject.messages WHERE msg_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    return result.fetchone()[0]


def get_op_date(m_id: int):
    """ Returns the activity_date of a selected message"""
    sql = "SELECT activity_date \
        FROM tsohaproject.messages \
        WHERE msg_id=:m_id"
    result = db.session.execute(sql, {"m_id":m_id})
    return result.fetchone()[0]

def get_reply_requested(m_id: int):
    """Returns reply request state for a single message"""
    sql = "SELECT reply_request \
        FROM tsohaproject.messages \
        WHERE msg_id=:m_id"
    result = db.session.execute(sql, {"m_id":m_id})
    return result.fetchone()[0]

def remove_reply_request(m_id: int):
    """ Sets reply request to False on a selected message"""
    sql = "UPDATE tsohaproject.messages \
        SET reply_request='False' \
        WHERE msg_id=:m_id"
    db.session.execute(sql, {"m_id":m_id})
    db.session.commit()

def fetch_message_senders():
    """Returns a list of volunteers that have sent at least one message"""
    sql = "SELECT DISTINCT(user_id), firstname, lastname \
        FROM tsohaproject.users LEFT JOIN tsohaproject.messages \
        ON users.user_id = volunteer_id \
        WHERE sender_id = users.user_id"
    result = db.session.execute(sql)
    return result.fetchall()

def check_reply_requests():
    """Returns True if there are reply requests"""
    sql = "SELECT COUNT(*) \
        FROM tsohaproject.messages \
        WHERE reply_request='True'"
    result = db.session.execute(sql)
    return bool(result.fetchone()[0] > 0)