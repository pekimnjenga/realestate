from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

class Listing(db.Model):
    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    size = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    images = db.Column(db.Text, nullable=False)  # Comma-separated filenames or JSON string
    
    #Helper method to easily loop through images in your templates.
    def get_image_list(self):
        return [img.strip() for img in self.images.split(',') if img.strip()]

#If you need to check the tables created in the database, you can use the following code snippet:
#from sqlalchemy import inspect
#inspector = inspect(db.engine)
#print(inspector.get_table_names())
