from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    sql = "SELECT users.user_id, users.role, password.password \
            FROM tsohaproject.users INNER JOIN tsohaproject.password \
            ON users.user_id = password.user_id \
            WHERE users.username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.user_id
            session["role"] = user.role
            return True
        else:
            return False
    
def create_admin(username: str, hash_value: str):
    try:
        sqlusers = "INSERT INTO tsohaproject.users (username,role,isactive) \
            VALUES (:username, :role, :isactive) RETURNING user_id"
        result = db.session.execute(sqlusers, \
            {"username":username, "role":'admin', "isactive": True})
        user_id = result.fetchone()[0]
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) \
            VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        db.session.commit()
    except:
        return render_template("register.html", show=True, \
            message="Something bad has happened, but I do not specifically know what. Try again.")

def is_admin():
    """Returns true if user is admin"""
    return user_role() is 'admin'

def is_coordinator():
    """If user is either coordinator or admin returns true"""
    return user_role() in ('admin', 'coordinator')

def is_volunteer():
    """If user is volunteer returns true"""
    return user_role() == 'volunteer'

def get_user_id():
    """Return id of logged in user"""
    u_id = session.get("user_id", 0)
    # print(f"user-id: {id}")
    return u_id

def get_role():
    """Return role of logged in user"""
    role = session.get("role", 0)
    return role

def user_role():
    """Returns role of logged in user differently"""
    u_id = get_user_id()
    if u_id != 0:
        sql = "SELECT role FROM tsohaproject.users WHERE user_id =:id"
        result = db.session.execute(sql, {"id":u_id})
        return result.fetchone()[0]
    return u_id

def logout():
    """Deletes user sessions"""
    del session["user_id"]
    del session["role"]

def password_valid(password1: str, password2: str):
    if len(password1) < 8:
        return [False, "Password must be atleast 8 characters long."]
        # render_template("register.html", show=True, \
        #     message="Password must be atleast 8 characters long.")
    if password1 != password2:
        return [False, "Passwords do not match, try again."]
        # render_template("register.html", show=True, \
        #     message="Passwords do not match, try again.")
    return [True, ""]

def validate_userinfo(params: list, qualifications: list):
    for i in params:
        if i is None or len(i) == 0:
            return [False, "One of the fields was empty. \
                    Please carefully fill in all fields."]
    qualifications_exists = False
    for qualification in qualifications:
        if qualification != "":
            noqualifications = True
    if not qualifications_exists:
        return [False, "Please select \
                atleast one qualification."]
    return [True, ""]

def create_useraccount(params: list, qualifications: list, hash_value: str):
    #Try is used here because one of the tables (users) has an unique column (username).
    #The commit contains multiple interts.
    try:
        sql = """INSERT INTO tsohaproject.users (lastname, firstname, email,
                startdate, role, username, isactive) 
                VALUES (:lastname, :firstname, :email, 
                :startdate, :role, :username, :isactive) 
                RETURNING user_id"""
        result = db.session.execute(sql, {"lastname": params[0], "firstname":params[1], \
            "email":params[2], "startdate":params[3], "role":params[4], \
                "username":params[5], "isactive":True})
        user_id = result.fetchone()[0]
        for task_id in qualifications:
            if task_id != "":
                sql = "INSERT INTO tsohaproject.volunteerqualification (task_id, user_id) \
                    VALUES (:task_id, :user_id)"
                db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) \
            VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        sqlactivity = "INSERT INTO tsohaproject.currentactivity (level_date, user_id, activity_id) \
            VALUES (:level_date, :user_id, :activitylevel)"
        db.session.execute(sqlactivity, {"level_date":params[3], "user_id":user_id, \
            "activitylevel":4})
        db.session.commit()
    except:
        return False
    return True