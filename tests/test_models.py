from app.models import Blog, Comment, Feature, Listing, Subscriber


def test_listing_image_list_and_numeric_price(app):
    with app.app_context():
        listing = Listing(
            name="Villa",
            location="Nairobi",
            description="Large plot",
            price="Ksh 5,000,000",
            image_urls="a.jpg, b.jpg, ,c.png",
        )
        # get_image_list should split and strip entries, dropping empties
        assert listing.get_image_list() == ["a.jpg", "b.jpg", "c.png"]

        # numeric_price should extract numeric portion
        assert listing.numeric_price == 5000000.0

        # Non-numeric prices should yield 0.0
        listing.price = "Not a number"
        assert listing.numeric_price == 0.0


def test_subscriber_repr_and_defaults(app):
    with app.app_context():
        s = Subscriber(email="foo@example.com")
        from app.extensions import db

        db.session.add(s)
        db.session.commit()

        # __repr__ uses the email
        assert repr(s) == f"<Subscriber {s.email}>"
        # Defaults applied on insert
        assert s.is_active is True
        assert s.date_joined is not None


def test_comment_defaults_and_replies(app):
    with app.app_context():
        from app.extensions import db

        blog = Blog(title="B", image_url=None, author="a", summary="s", content="c")
        db.session.add(blog)
        db.session.commit()

        parent = Comment(blog_id=blog.id, author_name="Parent", author_email="p@example.com", content="p")
        child = Comment(blog_id=blog.id, author_name="Child", author_email="c@example.com", content="c", parent=parent)

        db.session.add_all([parent, child])
        db.session.commit()

        # parent should have replies and defaults should be set
        assert list(parent.replies)
        assert child in list(parent.replies)
        assert parent.is_approved is True


def test_feature_listing_relationship(app):
    with app.app_context():
        from app.extensions import db

        f = Feature(name="Pool")
        listing = Listing(
            name="L",
            location="K",
            description="D",
            size="100 sqm",
            price="1000",
            image_urls="i.jpg",
        )
        db.session.add_all([f, listing])
        db.session.commit()

        listing.features.append(f)
        db.session.commit()

        # relationship backrefs should work
        assert f in list(listing.features)
        assert listing in list(f.listings)
