from datetime import date
from app import app
from flask import render_template, request, session
import error_handlers, messages

@app.route("/docs/aboutus")
def about_us():
    """Render About Us view"""
    return render_template("docs/aboutus.html")

@app.route("/docs/feedback")
def feedback():
    """Render feedback view"""
    return render_template("docs/feedback.html")

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Handle feedback submissions and render thank you view"""
    if session["csrf_token"] != request.form["csrf_token"]:
            return error_handlers.error("notauthorized")
    content = request.form["content"]
    fb_date = date.today()
    if len(content) == 0:
        return error_handlers.error('missing_value')
    messages.submit_feedback(fb_date, content)
    return render_template("/docs/thank-you.html")

@app.route("/success")
def success():
    return render_template("success.html")
