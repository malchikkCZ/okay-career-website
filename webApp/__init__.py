import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)

# Configure recaptcha
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdWtgwdAAAAAHTJUO2uRAT3vXzibvojmT--lgwz'
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get("RECAPTCHA_PRIVATE_KEY")

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///career'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

from webApp import routes
