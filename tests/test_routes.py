"""
Comprehensive test suite for Flask routes.
Tests cover: public pages, newsletters, blog comments, listing inquiries,
contact forms, admin operations, and authentication.
"""
# ruff: noqa: F841

import urllib.parse

from app.extensions import db
from app.models import (
    Blog,
    Comment,
    Listing,
    RequestSubmission,
    Subscriber,
)

# =============================================================================
# PUBLIC PAGE TESTS
# =============================================================================


class TestPublicPages:
    """Test public-facing routes accessible to all users."""

    def test_home_page(self, client):
        """Test that home page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"I Like It Properties" in response.data

    def test_contact_page(self, client):
        """Test that contact page is accessible."""
        response = client.get("/contact")
        assert response.status_code == 200

    def test_listings_page(self, client):
        """Test listings page with no filters."""
        response = client.get("/listings")
        assert response.status_code == 200

    def test_listings_page_with_filters(self, client, app, sample_listing):
        """Test listings page with location filter."""
        response = client.get("/listings?location=Kiamunyi")
        assert response.status_code == 200

    def test_blogs_index_page(self, client):
        """Test blogs listing page."""
        response = client.get("/blogs")
        assert response.status_code == 200

    def test_about_page(self, client):
        """Test about page."""
        response = client.get("/about")
        assert response.status_code == 200

    def test_sitemap(self, client):
        """Test sitemap.xml route."""
        response = client.get("/sitemap.xml")
        assert response.status_code == 200


# =============================================================================
# LISTING DETAIL TESTS
# =============================================================================


class TestListingDetail:
    """Test listing detail page and inquiry submission."""

    def test_listing_detail_page(self, client, app, sample_listing):
        """Test that listing detail page displays correctly."""
        response = client.get(f"/listing/{sample_listing.id}")
        assert response.status_code == 200
        assert b"Modern Villa" in response.data

    def test_listing_detail_404(self, client):
        """Test 404 for non-existent listing."""
        response = client.get("/listing/9999")
        assert response.status_code == 404

    def test_listing_inquiry_submission(self, client, app, sample_listing):
        """Test POST request to submit inquiry on listing."""
        response = client.post(
            f"/listing/{sample_listing.id}",
            data={
                "name": "John Doe",
                "email": "john@gmail.com",
                "message": "I'm interested in this property.",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Verify inquiry is saved to database
        with app.app_context():
            submission = RequestSubmission.query.first()
            assert submission is not None
            assert submission.name == "John Doe"
            assert submission.email == "john@gmail.com"

    def test_listing_inquiry_incomplete_form(self, client, sample_listing):
        """Test inquiry submission with missing fields."""
        response = client.post(
            f"/listing/{sample_listing.id}",
            data={"name": "John Doe"},  # Missing email and message
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Should show warning flash message
        assert b"Please complete all inquiry fields" in response.data or b"warning" in response.data


# =============================================================================
# BLOG DETAIL & COMMENT TESTS
# =============================================================================


class TestBlogDetail:
    """Test blog detail page and comment functionality."""

    def test_blog_detail_page(self, client, sample_blog):
        """Test that blog detail page displays correctly."""
        response = client.get(f"/blog/{sample_blog.id}")
        assert response.status_code == 200
        assert b"Test Blog Post" in response.data

    def test_blog_detail_404(self, client):
        """Test 404 for non-existent blog."""
        response = client.get("/blog/9999")
        assert response.status_code == 404

    def test_submit_comment_valid(self, client, app, sample_blog):
        """Test submitting a valid comment on a blog post."""
        response = client.post(
            f"/blog/{sample_blog.id}",
            data={
                "name": "Jane Smith",
                "email": "jane@gmail.com",
                "message": "Great post! Very informative.",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Verify comment is created (but not approved yet)
        with app.app_context():
            comment = Comment.query.filter_by(blog_id=sample_blog.id).first()
            assert comment is not None
            assert comment.author_name == "Jane Smith"
            assert comment.author_email == "jane@gmail.com"
            assert comment.is_approved is False  # Awaiting moderation

    def test_submit_comment_gmail_only(self, client, app, sample_blog):
        """Test that non-Gmail emails are rejected for comments."""
        response = client.post(
            f"/blog/{sample_blog.id}",
            data={
                "name": "Bob",
                "email": "bob@yahoo.com",  # Not Gmail
                "message": "Nice article.",
            },
            follow_redirects=True,
        )
        # Should reject non-Gmail addresses
        assert b"Gmail address" in response.data or b"warning" in response.data

    def test_submit_comment_without_name(self, client, sample_blog):
        """Test comment submission with missing name field."""
        response = client.post(
            f"/blog/{sample_blog.id}",
            data={
                "email": "user@gmail.com",
                "message": "Comment text",
            },
            follow_redirects=True,
        )
        # Should show validation error
        assert b"warning" in response.data or b"valid" in response.data

    def test_honeypot_field(self, client, sample_blog):
        """Test that honeypot field blocks spam submissions."""
        response = client.post(
            f"/blog/{sample_blog.id}",
            data={
                "name": "Spammer",
                "email": "spam@gmail.com",
                "message": "Spam message",
                "confirm_email_address": "yes",  # Honeypot field should be empty
            },
            follow_redirects=True,
        )
        # Should redirect without creating comment
        with db.session.begin_nested():
            comment_count = Comment.query.filter_by(blog_id=sample_blog.id, author_name="Spammer").count()
            assert comment_count == 0

    def test_comment_sanitization(self, client, app, sample_blog):
        """Test that HTML is sanitized from comments."""
        response = client.post(
            f"/blog/{sample_blog.id}",
            data={
                "name": "User",
                "email": "user@gmail.com",
                "message": "<script>alert('xss')</script>Safe text",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            comment = Comment.query.filter_by(blog_id=sample_blog.id).first()
            assert comment is not None
            # Script tag should be stripped
            assert "<script>" not in comment.content
            assert "Safe text" in comment.content


# =============================================================================
# NEWSLETTER SUBSCRIPTION TESTS
# =============================================================================


class TestNewsletterSubscription:
    """Test newsletter subscription and unsubscription."""

    def test_subscribe_new_email(self, client, app):
        """Test subscribing a new email to newsletter."""
        response = client.post(
            "/subscribe",
            data={"email": "newsubscriber@gmail.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            subscriber = Subscriber.query.filter_by(email="newsubscriber@gmail.com").first()
            assert subscriber is not None
            assert subscriber.is_active is True

    def test_subscribe_already_subscribed(self, client, app, sample_subscriber):
        """Test subscribing an already-subscribed email."""
        response = client.post(
            "/subscribe",
            data={"email": sample_subscriber.email},
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Should show info message about already subscribed
        assert b"already subscribed" in response.data or b"info" in response.data

    def test_subscribe_reactivate_unsubscribed(self, client, app):
        """Test reactivating an unsubscribed email."""
        with app.app_context():
            subscriber = Subscriber(email="lapsed@gmail.com", is_active=False)
            db.session.add(subscriber)
            db.session.commit()

        response = client.post(
            "/subscribe",
            data={"email": "lapsed@gmail.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            subscriber = Subscriber.query.filter_by(email="lapsed@gmail.com").first()
            assert subscriber.is_active is True

    def test_subscribe_empty_email(self, client):
        """Test subscribing without providing an email."""
        response = client.post("/subscribe", data={"email": ""}, follow_redirects=True)
        assert response.status_code == 200
        # Should show warning
        assert b"warning" in response.data or b"email" in response.data

    def test_unsubscribe_subscriber(self, client, app, sample_subscriber):
        """Test unsubscribing a subscriber."""
        email_encoded = urllib.parse.quote(sample_subscriber.email, safe="")
        response = client.get(f"/unsubscribe/{email_encoded}")
        assert response.status_code == 200

        with app.app_context():
            subscriber = Subscriber.query.filter_by(email=sample_subscriber.email).first()
            assert subscriber.is_active is False

    def test_unsubscribe_nonexistent_email(self, client):
        """Test unsubscribing a non-existent email."""
        response = client.get("/unsubscribe/nonexistent@gmail.com")
        assert response.status_code == 404


# =============================================================================
# CONTACT FORM TESTS
# =============================================================================


class TestContactForm:
    """Test contact form submission."""

    def test_contact_form_submission_valid(self, client, app):
        """Test submitting a valid contact form."""
        response = client.post(
            "/contact",
            data={
                "name": "Contact User",
                "email": "contact@gmail.com",
                "subject": "Website Inquiry",
                "message": "I have a question about your services.",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            submission = RequestSubmission.query.filter_by(email="contact@gmail.com").first()
            assert submission is not None
            assert submission.subject == "Website Inquiry"

    def test_contact_form_invalid_email(self, client):
        """Test contact form with invalid email."""
        response = client.post(
            "/contact",
            data={
                "name": "User",
                "email": "invalid-email",
                "subject": "Subject",
                "message": "Message",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Should show error for invalid email
        assert b"correctly" in response.data or b"danger" in response.data

    def test_contact_form_missing_fields(self, client):
        """Test contact form with missing required fields."""
        response = client.post(
            "/contact",
            data={"name": "User", "email": "user@gmail.com"},  # Missing subject and message
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"danger" in response.data or b"fill all fields" in response.data


# =============================================================================
# AUTHENTICATION & ADMIN TESTS
# =============================================================================


class TestAuthentication:
    """Test user authentication (login/logout)."""

    def test_login_page_accessible(self, client):
        """Test that login page is accessible."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_valid_credentials(self, client, app, admin_user):
        """Test login with valid credentials."""
        response = client.post(
            "/login",
            data={"username": "admin", "password": "password123"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post("/login", data={"username": "admin", "password": "wrongpassword"})
        assert response.status_code == 200
        assert b"Invalid" in response.data or b"Denied" in response.data

    def test_logout(self, client, admin_client):
        """Test logout functionality."""
        response = admin_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200

    def test_admin_dashboard_requires_login(self, client):
        """Test that admin dashboard requires login."""
        response = client.get("/admin/dashboard")
        # Should redirect to login
        assert response.status_code in [302, 303, 401]

    def test_admin_dashboard_accessible_when_logged_in(self, client, admin_client):
        """Test that admin can access dashboard when logged in."""
        response = admin_client.get("/admin/dashboard")
        assert response.status_code == 200


# =============================================================================
# ADMIN BLOG TESTS
# =============================================================================


class TestAdminBlog:
    """Test admin blog creation, editing, and deletion."""

    def test_admin_blogs_list(self, client, admin_client, sample_blog):
        """Test admin can view blogs list."""
        response = admin_client.get("/admin/blogs")
        assert response.status_code == 200
        assert b"Test Blog Post" in response.data

    def test_create_blog_post(self, client, admin_client, app, sample_category):
        """Test creating a new blog post."""
        response = admin_client.post(
            "/admin/blog/new",
            data={
                "title": "New Tech Blog",
                "content": "This is a detailed tech article.",
                "category": "Tech Updates",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            blog = Blog.query.filter_by(title="New Tech Blog").first()
            assert blog is not None

    def test_create_blog_without_login(self, client):
        """Test that non-logged-in users cannot create blogs."""
        response = client.get("/admin/blog/new")
        # Should redirect to login
        assert response.status_code in [302, 303, 401]

    def test_edit_blog_post(self, client, admin_client, app, sample_blog):
        """Test editing an existing blog post."""
        response = admin_client.post(
            f"/admin/blog/edit/{sample_blog.id}",
            data={
                "title": "Updated Blog Title",
                "content": "Updated blog content.",
                "category": "Market Updates",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            blog = Blog.query.get(sample_blog.id)
            assert blog.title == "Updated Blog Title"

    def test_delete_blog_post(self, client, admin_client, app, sample_blog):
        """Test deleting a blog post."""
        blog_id = sample_blog.id
        response = admin_client.post(
            f"/admin/blog/delete/{blog_id}",
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            blog = Blog.query.get(blog_id)
            assert blog is None


# =============================================================================
# ADMIN LISTING TESTS
# =============================================================================


class TestAdminListing:
    """Test admin listing creation, editing, and deletion."""

    def test_admin_listings_list(self, client, admin_client, sample_listing):
        """Test admin can view listings."""
        response = admin_client.get("/admin/listings")
        assert response.status_code == 200
        assert b"Modern Villa" in response.data

    def test_create_listing(self, client, admin_client, app, sample_features):
        """Test creating a new listing."""
        response = admin_client.post(
            "/admin/listing/new",
            data={
                "name": "New Property",
                "location": "Nairobi",
                "description": "A new property.",
                "size": "1000 sqft",
                "price": "Ksh 5,000,000",
                "property_type": "Residential",
                "listing_status": "For Sale",
                "bedrooms": 3,
                "bathrooms": 2,
                "features_list": "Swimming Pool, CCTV Security",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            listing = Listing.query.filter_by(name="New Property").first()
            assert listing is not None

    def test_edit_listing(self, client, admin_client, app, sample_listing):
        """Test editing an existing listing."""
        response = admin_client.post(
            f"/admin/listing/edit/{sample_listing.id}",
            data={
                "name": "Updated Property Name",
                "location": "Kiamunyi",
                "description": "Updated description.",
                "size": "6000 sqft",
                "price": "Ksh 20,000,000",
                "property_type": "Residential",
                "listing_status": "For Sale",
                "bedrooms": 6,
                "bathrooms": 5,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            listing = Listing.query.get(sample_listing.id)
            assert listing.name == "Updated Property Name"

    def test_delete_listing(self, client, admin_client, app, sample_listing):
        """Test deleting a listing."""
        listing_id = sample_listing.id
        response = admin_client.post(
            f"/admin/listing/delete/{listing_id}",
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            listing = Listing.query.get(listing_id)
            assert listing is None

    def test_toggle_listing_sold_status(self, client, admin_client, app, sample_listing):
        """Test toggling listing sold status."""
        response = admin_client.post(
            f"/admin/listing/{sample_listing.id}/toggle_sold",
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            listing = Listing.query.get(sample_listing.id)
            assert listing.is_sold is True


# =============================================================================
# ADMIN COMMENT MODERATION TESTS
# =============================================================================


class TestCommentModeration:
    """Test admin comment approval, deletion, and replies."""

    def test_pending_comments_page(self, client, admin_client):
        """Test admin can view pending comments."""
        response = admin_client.get("/admin/comments")
        assert response.status_code == 200

    def test_approve_comment(self, client, admin_client, app, sample_blog):
        """Test approving a pending comment."""
        # First, create a comment
        with app.app_context():
            comment = Comment(
                author_name="Test User",
                author_email="user@gmail.com",
                content="Great blog post!",
                blog_id=sample_blog.id,
                is_approved=False,
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id

        # Now approve it
        response = admin_client.get(
            f"/admin/comment/approve/{comment_id}",
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            comment = Comment.query.get(comment_id)
            assert comment.is_approved is True

    def test_delete_comment(self, client, admin_client, app, sample_blog):
        """Test deleting a comment."""
        with app.app_context():
            comment = Comment(
                author_name="Spam User",
                author_email="spam@gmail.com",
                content="Spam comment",
                blog_id=sample_blog.id,
                is_approved=False,
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id

        response = admin_client.get(
            f"/admin/comment/delete/{comment_id}",
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            comment = Comment.query.get(comment_id)
            assert comment is None

    def test_reply_to_comment(self, client, admin_client, app, sample_blog):
        """Test admin replying to a comment."""
        with app.app_context():
            comment = Comment(
                author_name="User",
                author_email="user@gmail.com",
                content="Question about the post?",
                blog_id=sample_blog.id,
                is_approved=True,
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id

        response = admin_client.post(
            f"/admin/comment/reply/{comment_id}",
            data={"reply_content": "Thanks for your question! Here's the answer..."},
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            replies = Comment.query.filter_by(parent_id=comment_id).all()
            assert len(replies) > 0
            assert "answer" in replies[0].content
