"""setup_db.py

Create DB tables and a default admin user. Uses create_app() to build
an application context so SQLAlchemy works correctly.
"""

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created successfully.")

    # Check if admin user already exists
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("yourpassword"),  # Replace with your secure password
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created.")
    else:
        print("ℹ️ Admin user already exists.")
