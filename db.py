import os
from flask_sqlalchemy import SQLAlchemy
from app import app

# Had issues with running the app in Heroku. This fixed the issue.
uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

#app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)
