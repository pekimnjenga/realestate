from app.extensions import db
from app.models import Blog, Listing


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_contact_page(client):
    response = client.get("/contact")
    assert response.status_code == 200


def test_listings_page(client):
    response = client.get("/listings")
    assert response.status_code == 200


def test_listing_detail_page(client, app):
    with app.app_context():
        listing = Listing(
            name="Villa",
            location="Nairobi",
            description="Spacious",
            price=500000,
            size="2000 sqft",
            image_urls="img1.jpg,img2.jpg",
            sold_at=None,
        )
        db.session.add(listing)
        db.session.flush()
        listing_id = listing.id
        db.session.commit()

    response = client.get(f"/listing/{listing_id}")
    assert response.status_code == 200


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_blog_page(client, app):
    with app.app_context():
        blog = Blog(
            title="New Blog",
            image_url="image.jpg",
            author="Admin",
            summary="Summary",
            content="Content",
            date_posted=None,
        )
        db.session.add(blog)
        db.session.flush()
        blog_id = blog.id
        db.session.commit()

    response = client.get(f"/blog/{blog_id}")
    assert response.status_code == 200
