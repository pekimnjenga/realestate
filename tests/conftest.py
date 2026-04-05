import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Blog, Category, Feature, Listing, Subscriber, User


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,  # Disable CSRF checks for testing
            "MAIL_SUPPRESS_SEND": True,  # Don't actually send emails during testing
        }
    )
    with app.app_context():
        db.create_all()
        # Prevent SQLAlchemy from expiring objects on commit so fixtures
        # returned to tests remain attached to the session during requests.
        # This makes fixture instances safe to use across the test client.
        try:
            db.session.expire_on_commit = False  # type: ignore[attr-defined]
        except Exception:
            pass
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create and return an admin user for testing."""
    with app.app_context():
        admin = User(
            username="admin",
            password=generate_password_hash("password123"),
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()
        # Return a fresh, session-bound instance
        return User.query.get(admin.id)


@pytest.fixture
def regular_user(app):
    """Create and return a regular (non-admin) user for testing."""
    with app.app_context():
        user = User(
            username="testuser",
            password=generate_password_hash("userpass123"),
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()
        return User.query.get(user.id)


@pytest.fixture
def admin_client(app, admin_user):
    """Return a test client with admin user logged in."""
    client = app.test_client()
    # Log in the admin user
    with client:
        client.post(
            "/login",
            data={"username": "admin", "password": "password123"},
            follow_redirects=True,
        )
    return client


@pytest.fixture
def sample_category(app):
    """Create a sample blog category."""
    with app.app_context():
        category = Category(name="Market Updates")
        db.session.add(category)
        db.session.commit()
        return Category.query.get(category.id)


@pytest.fixture
def sample_blog(app, sample_category, admin_user):
    """Create a sample blog post."""
    with app.app_context():
        blog = Blog(
            title="Test Blog Post",
            image_url="test.jpg",
            author=admin_user.username,
            summary="A test blog summary.",
            content="This is the full content of the test blog post.",
            category_id=sample_category.id,
        )
        db.session.add(blog)
        db.session.commit()
        return Blog.query.get(blog.id)


@pytest.fixture
def sample_listing(app):
    """Create a sample property listing."""
    with app.app_context():
        listing = Listing(
            name="Modern Villa",
            description="A beautiful modern villa in Nairobi.",
            location="Kiamunyi",
            size="5000 sqft",
            price="Ksh 15,000,000",
            property_type="Residential",
            listing_status="For Sale",
            bedrooms=5,
            bathrooms=4,
            image_urls="villa1.jpg,villa2.jpg",
        )
        db.session.add(listing)
        db.session.commit()
        return Listing.query.get(listing.id)


@pytest.fixture
def sample_features(app):
    """Create sample amenities/features."""
    with app.app_context():
        features = [
            Feature(name="Swimming Pool"),
            Feature(name="CCTV Security"),
            Feature(name="Backup Power"),
        ]
        db.session.add_all(features)
        db.session.commit()
        # Return fresh, bound feature instances
        return [Feature.query.get(f.id) for f in features]


@pytest.fixture
def sample_subscriber(app):
    """Create a sample subscriber."""
    with app.app_context():
        subscriber = Subscriber(email="subscriber@gmail.com")
        db.session.add(subscriber)
        db.session.commit()
        return Subscriber.query.get(subscriber.id)
