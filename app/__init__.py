from flask import Flask
from app.routes import main
from app.models import db, User
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import secrets
import os


app = Flask(__name__, static_folder='static', template_folder='templates')
app.register_blueprint(main)
app.secret_key = secrets.token_hex(32) #Secret key for session management
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'  # redirect if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Data scientist.@localhost:5432/realestate_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  # or your preferred DB

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

db.init_app(app)
