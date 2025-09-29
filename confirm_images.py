from app import create_app
from app.models import Listing

app = create_app()

with app.app_context():
    listings = Listing.query.all()
    for listing in listings:
        print(f"{listing.id}: {listing.image_urls}")
