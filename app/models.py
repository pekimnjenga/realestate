from datetime import datetime
from typing import TYPE_CHECKING, Any

from flask_login import UserMixin

from app.extensions import db

if TYPE_CHECKING:  # Help static type checkers understand SQLAlchemy's declarative base
    Base = Any
else:
    Base = db.Model

# ==========================================
# ASSOCIATION TABLES
# ==========================================

# Many-to-Many relationship between Listings and Features
# This allows a single listing to have many features (e.g., Gym, Pool, Backup Power)
# and a single feature to be associated with many listings.
listing_features = db.Table(
    "listing_features",
    db.Column("listing_id", db.Integer, db.ForeignKey("listings.id"), primary_key=True),
    db.Column("feature_id", db.Integer, db.ForeignKey("feature.id"), primary_key=True),
)

# ==========================================
# USER & AUTHENTICATION
# ==========================================


class User(Base, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


# ==========================================
# BLOG SYSTEM
# ==========================================


class Category(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True)
    # Allows calling category.blogs to get all posts in that category
    blogs = db.relationship("Blog", backref="category_rel", lazy=True)


class Blog(Base):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    author = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    # cascade="all, delete-orphan" ensures comments are removed if the blog is deleted
    comments = db.relationship("Comment", backref="blog", lazy=True, cascade="all, delete-orphan")


class Comment(Base):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.id"), nullable=True)
    author_name = db.Column(db.String(100), nullable=True)
    author_email = db.Column(db.String(120), nullable=True)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"), nullable=True)
    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id]),
        lazy=True,
        cascade="all, delete-orphan",
    )

    # SECURITY: Set to False by default for manual admin moderation
    is_approved = db.Column(db.Boolean, default=True)
    is_seen = db.Column(db.Boolean, default=False)
    # Whether the comment was flagged by the profanity filter
    is_flagged = db.Column(db.Boolean, default=False)
    # Whether the author of this comment/reply is an admin (prevents impersonation)
    author_is_admin = db.Column(db.Boolean, default=False)
    # Whether the comment submitter has verified ownership of the email
    email_verified = db.Column(db.Boolean, default=False)


# ==========================================
# PROPERTY LISTING ENGINE
# ==========================================


class Feature(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True)  # e.g., "Swimming Pool", "3-Phase Power"


class Listing(Base):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    size = db.Column(db.Text, nullable=False)  # e.g., "5000 sqft" or "0.5 Acres"
    price = db.Column(db.String(50), nullable=False)

    # CORE FILTERS
    # Options: 'Residential', 'Commercial', 'Industrial', 'Land'
    property_type = db.Column(db.String(50), nullable=True, default="Residential")
    # Options: 'For Sale', 'For Rent'
    listing_status = db.Column(db.String(20), nullable=True, default="For Sale")

    # DYNAMIC SPECS (Nullable to accommodate different property types)
    bedrooms = db.Column(db.Integer, nullable=True)  # For Residential
    bathrooms = db.Column(db.Integer, nullable=True)  # For Residential
    floors = db.Column(db.Integer, nullable=True)  # For Commercial/Residential
    parking_spaces = db.Column(db.Integer, nullable=True)  # For Commercial/Industrial
    year_built = db.Column(db.Integer, nullable=True)

    # ASSETS & STATUS
    image_urls = db.Column(db.Text, nullable=False)  # Comma-separated filenames
    is_sold = db.Column(db.Boolean, default=False)
    sold_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    features = db.relationship(
        "Feature",
        secondary=listing_features,
        backref=db.backref("listings", lazy="dynamic"),
    )

    def get_image_list(self):
        """Helper to convert comma-separated string to a list for templates."""
        return [img.strip() for img in self.image_urls.split(",") if img.strip()]

    @property
    def numeric_price(self):
        """Extracts numeric value from price string (e.g., 'KSh 5,000' -> 5000)."""
        import re

        try:
            return float(re.sub(r"[^\d.]", "", str(self.price)))
        except (ValueError, TypeError):
            return 0.0


# ==========================================
# FORMS & INQUIRIES
# ==========================================


class RequestSubmission(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscriber(Base):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Useful for 'Unsubscribe' links

    def __repr__(self):
        return f"<Subscriber {self.email}>"


# If you need to check the tables created in the database, you can use the following code snippet:
# from sqlalchemy import inspect
# inspector = inspect(db.engine)
# print(inspector.get_table_names())
