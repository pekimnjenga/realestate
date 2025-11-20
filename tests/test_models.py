from app.models import Blog, Listing


def test_listing_model_fields(app):
    with app.app_context():
        listing = Listing(
            name="Villa", location="Nairobi", description="Large plot", price=500000
        )
        assert listing.name == "Villa"
        assert listing.price == 500000
        assert listing.location == "Nairobi"
        assert listing.description == "Large plot"


def test_blog_model_fields(app):
    with app.app_context():
        blog = Blog(
            title="Test Blog",
            image_url="image.jpg",
            author="PEKIM",
            summary="This is a summary.",
            content="This is the full content.",
            date_posted=None,
        )

        assert blog.title == "Test Blog"
        assert blog.image_url == "image.jpg"
        assert blog.author == "PEKIM"
        assert blog.summary == "This is a summary."
        assert blog.content == "This is the full content."
        assert blog.date_posted is None
