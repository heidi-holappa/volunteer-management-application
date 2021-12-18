from app import app
from flask import render_template, request
from datetime import datetime, timezone
import hrqueries, users

@app.errorhandler(404)
def not_found(e):
    """Shown when user tries to access a path that does not exist. Logs url, user_id"""
    log_action(f"Not found:{e};route:{request.url};user_id:{users.get_user_id()}")
    instructions = ""
    return render_template("error.html", error="The page you requested was not found.", 
    error_time=datetime.now(timezone.utc), details=e, instructions=instructions)

@app.errorhandler(403)
def forbidden(e):
    """"Shown when user tries to access content they're not authorized to access"""
    log_action(f"Forbidden:{e};route:{request.url};user_id:{users.get_user_id()}")
    instructions = "This error is most likely due to insufficient rights. \
        Please make sure that you have the right to access the content you tried to access. \
        Contact system administrator for more support."
    return render_template("error.html", error="The content you tried to access is forbidden", 
    error_time=datetime.now(timezone.utc), details=e, instructions=instructions)

def log_action(content: str):
    """Creates a log-event in the database."""
    u_id = users.get_user_id()
    if u_id == 0:
        u_id = 1
        hrqueries.log_mark([u_id, datetime.now(timezone.utc), f"No user id: {content}"])
    else: 
        hrqueries.log_mark([u_id, datetime.now(timezone.utc), content])

