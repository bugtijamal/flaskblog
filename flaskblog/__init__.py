
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_msearch import Search

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY']='thisisatopsecretsforme'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)

login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.login_message_category = "info"

from flaskblog import routes