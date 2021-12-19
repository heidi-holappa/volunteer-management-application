from datetime import date
from flask import flash, render_template, redirect, request, session, abort
from app import app
import messages
import users

@app.route("/docs/aboutus")
def about_us():
    """Render About Us view"""
    rply_requests = messages.check_reply_requests()
    return render_template("docs/aboutus.html", rply_requests=rply_requests)

@app.route("/docs/feedback")
def feedback():
    """Render feedback view"""
    rply_requests = messages.check_reply_requests()
    return render_template("docs/feedback.html", rply_requests=rply_requests)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Handle feedback submissions and render thank you view"""
    if users.get_user_id() != 0:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
    content = request.form["content"]
    fb_date = date.today()
    if len(content) == 0:
        flash("The feedback must atleast one character.", "danger")
        return redirect("/docs/feedback")
    messages.submit_feedback(fb_date, content)
    flash("Feedback sent successfully", "success")
    return render_template("/docs/thank-you.html")

@app.route("/success")
def success():
    rply_requests = messages.check_reply_requests()
    return render_template("success.html", rply_requests=rply_requests)
