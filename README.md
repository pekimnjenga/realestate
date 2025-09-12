A dynamic real estate website built with Flask, HTML, and CSS, designed to showcase property listings and blog posts. The site is divided into two main interfaces:
-User Interface – Public-facing pages for browsing listings, reading blogs, and learning about the company

-Admin Interface – Secure backend for managing listings and blog content (add/update/delete)

#Project's structure
real-estate-website/
├── app/
│   ├── __init__.py
|   ├── __pycache__
│   ├── routes.py │ 
│   ├── models.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── images/
│   │   └── uploads/           #Listing images are manually uploaded to this folder
│   └── templates/
│        ├── base.html/
│        ├── user/
│        │   ├── about.html
│        │   ├── listings.html
│        │   ├── blogs.html
│        │   ├── home.html
│        │   ├── contact.html
│        │   ├── blog_detail.html
│        │   └──listing_detail.html
│        └── admin/
│            ├── login.html
│            ├── new_listing.html
│            ├── admin_dashboard.html
│            ├── admin_blogs.html
│            ├── admin_listings.html
│            ├── edit_blog.html
│            ├── edit_listing.html
│            └── new_blog.html
│          
├── migrations
├── venv
├── .dockerignore
├── Dockerfile
├── render.yml
├── requirements.txt
├── run.py
└── README.md
