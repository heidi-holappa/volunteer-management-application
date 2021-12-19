from db import db
from flask import session
import secrets
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    """User login"""
    sql = "SELECT users.user_id, users.role, password.password \
            FROM tsohaproject.users INNER JOIN tsohaproject.password \
            ON users.user_id = password.user_id \
            WHERE users.username=:username AND isactive='True'"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.user_id
            session["role"] = user.role
            session["csrf_token"] = secrets.token_hex(16)
            return True
        else:
            return False
    

def create_admin(username: str, hash_value: str):
    """Create an admin level account"""
    try:
        sqlusers = "INSERT INTO tsohaproject.users (username,role,isactive) \
            VALUES (:username, :role, :isactive) RETURNING user_id"
        result = db.session.execute(sqlusers, \
            {"username":username, "role":"admin", "isactive": True})
        user_id = result.fetchone()[0]
        sqlpassword = "INSERT INTO tsohaproject.password (user_id, password) \
            VALUES (:user_id, :password)"
        db.session.execute(sqlpassword, {"user_id":user_id, "password":hash_value})
        db.session.commit()
        return True
    except:
        return False

def is_admin():
    """Returns true if logged in user is admin"""
    return user_role() == 'admin'

def is_coordinator():
    """If logged in user is either coordinator or admin returns true"""
    return user_role() in ('admin', 'coordinator')

def is_volunteer():
    """If logged in user is volunteer returns true"""
    return user_role() == 'volunteer'

def is_volunteer_with_id(u_id):
    """Return true, if user with given id has role volunteer"""
    sql = "SELECT role FROM tsohaproject.users WHERE user_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    return bool(result.fetchone()[0] == "volunteer")

def get_user_id():
    """Return id of logged in user"""
    u_id = session.get("user_id", 0)
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

def get_name(u_id):
    """Return the first and lastname of the given user_id"""
    sql = "SELECT firstname, lastname \
        FROM tsohaproject.users \
        WHERE user_id=:id"
    result = db.session.execute(sql, {"id":u_id})
    get_result = result.fetchone()
    return f"{get_result[0]} {get_result[1]}"

def logout():
    """Deletes user sessions"""
    del session["user_id"]
    del session["role"]
    del session["csrf_token"]

def password_valid(password1: str, password2: str):
    return bool(len(password1) >= 8 and password1 == password2)

def validate_userinfo(params: list, qualifications: list):
    for i in params:
        if i is None or len(str(i)) == 0:
            return False
    qualifications_exists = False
    for qualification in qualifications:
        if qualification != "":
            qualifications_exists = True
    if not qualifications_exists:
        return False
    return True

def update_password(old: str, new: str, new_confirmed: str):
    validate_pw = password_valid(new, new_confirmed)
    if not validate_pw:
        return False
    u_id = get_user_id()
    sql = "SELECT password FROM tsohaproject.password \
        WHERE user_id=:id"
    old_fetched = db.session.execute(sql, {"id":u_id}).fetchone()[0]
    if check_password_hash(old, old_fetched):
        return False
    hash_value = generate_password_hash(new)
    sql = "UPDATE tsohaproject.password SET password=:password WHERE user_id=:id"
    db.session.execute(sql, {"password":hash_value, "id":u_id})
    db.session.commit()
    return True

def create_useraccount(params: list, qualifications: list, hash_value: str):
    """Try is used here because one of the tables (users) has an unique column (username)."""
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
        db.session.execute(sqlactivity, {"level_date":params[6], "user_id":user_id, \
            "activitylevel":3})
        db.session.commit()
    except:
        return False
    return True


