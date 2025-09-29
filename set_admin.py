# set_admin.py
import os
from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = create_app()

with app.app_context():
    username = os.getenv('ADMIN_USERNAME')
    password = os.getenv('ADMIN_PASSWORD')
    # Check if admin user already exists
    if not User.query.filter_by(username='username').first():
        admin = User(
            username= username,
            password=generate_password_hash(password), 
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
