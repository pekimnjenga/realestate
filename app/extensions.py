import os

from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
cache = Cache()
# Allow configuring limiter storage via env (e.g. redis). Default to in-memory for small sites.
_ratelimit_storage = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
limiter = Limiter(key_func=get_remote_address, storage_uri=_ratelimit_storage)
