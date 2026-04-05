import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True") == "True"
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    BASE_URL = os.environ.get("BASE_URL")
    # URL building settings (useful for generating absolute links in emails)
    # Set these in your environment for production (e.g., 'example.com').
    SERVER_NAME = os.environ.get("SERVER_NAME")  # e.g. 'example.com' or 'example.com:5000'
    APPLICATION_ROOT = os.environ.get("APPLICATION_ROOT", "/")
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")
    # Default timeout for cached items (seconds). Can be overridden via env.
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))
