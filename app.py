from os import getenv
from flask import Flask

app = Flask(__name__)

# from dotenv import load_dotenv
# load_dotenv()
app.secret_key = getenv("SECRET_KEY")

import routes
