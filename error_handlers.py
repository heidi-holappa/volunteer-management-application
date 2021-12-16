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

def error(description):
    """Render Error view"""
    message = "This is a general error message. Something caused an error, but there is not \
        enough information to tell what. Feedback on the error would be appreciated! \
            We apologize for the inconvenience."
    if description == 'notauthorized':
        message = 'You have tried to access a page that you are not authorized to view. \
            Please make sure you are logged in. If the problem continues, \
                please leave feedback on the issue. Feedback form can be found in the footer.'
    if description == 'missing_value':
        message = 'One or more fields were left empty. Please fill in all fields carefully.'
    log_action(f"Landed on errorpage. Errormessage received: {message}")
    return render_template("error.html", error=message, details="", instructions="")

def log_action(content: str):
    """Creates a log-event in the database."""
    u_id = users.get_user_id()
    if u_id == 0:
        u_id = 1
        hrqueries.log_mark([u_id, datetime.now(timezone.utc), f"No user id: {content}"])
    else: 
        hrqueries.log_mark([u_id, datetime.now(timezone.utc), content])

