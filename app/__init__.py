import secrets

from flask import Flask

from app.extensions import db, login_manager, migrate
from app.routes import main
from config import Config


def create_app(config=None):
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load default config
    app.config.from_object(Config)

    # Apply overrides (e.g. test settings)
    if config:
        app.config.update(config)

    # Override secret key dynamically if needed
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or secrets.token_hex(32)

    # Add engine options
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

    # Init extensions AFTER config is finalized
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    # Register blueprints
    app.register_blueprint(main)

    # User loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
