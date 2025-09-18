from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config  # Import your config class
import secrets

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Load configuration from Config class
    app.config.from_object(Config)

    # Optional: Override secret key dynamically if needed
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY') or secrets.token_hex(32)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # User loader
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
