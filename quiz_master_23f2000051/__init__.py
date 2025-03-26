from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.sqlite3'
app.config['SECRET_KEY'] = '988270e57f7ee38cceb56e04e8388c3f'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from quiz_master_23f2000051.controllers import admin
from quiz_master_23f2000051.controllers import auth
from quiz_master_23f2000051.controllers import users