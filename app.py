from os import getenv
import os
import re
from datetime import datetime, date, timezone
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# from dotenv import load_dotenv
# load_dotenv()
app.secret_key = getenv("SECRET_KEY")

import routes