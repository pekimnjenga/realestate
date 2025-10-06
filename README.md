### NAME OF THE WEBSITE 
ilikeitproperties
### BRANCH 
Production
### PROJECT'S BRIEF DESCRIPTION
A dynamic real estate website built with Flask, HTML, Bootstrap 5 classes and CSS, designed to showcase property listings and blog posts and also for users to make inquiries about the listings. The site is divided into two main interfaces:

-User Interface – Public-facing pages for browsing listings, making inquiries about the listings or any other matter, reading blogs, and learning about the company

-Admin Interface – Secure backend for managing listings and blog content (add/update/delete)

### TOOLS USED
- Flask
- HTML
- CSS
- Bootstrap 5
- Github actions
- Cloudflare r2 - For hosting my images and other static files
- Truehost Server - Hosting my website
- Truehost's Postgres Database - Hosting my database
- Github Copilot

### PROJECT'S STRUCTURE
real-estate-website/
├── config.py
├── confirm_images.py
├── README.md
├── requirements.txt
├── run.py
├── set_admin.py
├── .github/
│   └── workflows/
│       └── deploy.yml
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── images/
│   │       ├── corevalues.png
│   │       ├── growth.png
│   │       ├── handshake.png
│   │       ├── IMG-20250831-WA0012.jpg
│   │       ├── Jacob.jpg
│   │       ├── logo.jpg
│   │       ├── mission.png
│   │       ├── realestateimage.jpeg
│   │       └── vision.png
│   ├── templates/
│   │   ├── base.html
│   │   ├── admin/
│   │   │   ├── admin_blogs.html
│   │   │   ├── admin_dashboard.html
│   │   │   ├── admin_listings.html
│   │   │   ├── edit_blog.html
│   │   │   ├── edit_listing.html
│   │   │   ├── login.html
│   │   │   ├── new_blog.html
│   │   │   └── new_listing.html
│   │   └── user/
│   │       ├── about.html
│   │       ├── blog_detail.html
│   │       ├── blogs.html
│   │       ├── contact.html
│   │       ├── home.html
│   │       ├── listing_detail.html
│   │       └── listings.html
│   └── utils/
│       └── r2_upload.py
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── 6e2a4d3fde84_adding_new_columns_to_my_models_and_.py


### DEPLOYMENT STRATEGY
Unlike the staging branch (which uses Render’s auto-deploy), I manually configured the production branch to deploy to Truehost using GitHub Actions each time a push is made.

## Production Deployment via GitHub Actions

### Setup
- Created `.github/workflows/deploy.yml`
- Added FTP credentials to GitHub Secrets
- Defined local/server directories and exclusions

### Python App Configuration on Truehost
- Created Python application in cPanel
- Set:
  - Application Root
  - Application URL
  - Startup File: `run.py`
  - Entry Point: `app`
- Added environment variables (e.g. `DATABASE_URL`, `R2_ACCESS_KEY`, etc.)

### Deployment Flow
- Push to `main` triggers GitHub Actions
- Code is deployed to Truehost via FTP
- Dependencies installed via cPanel terminal
- App runs live on production domain


## 👨‍💻 Developer Contact

Developed and maintained by **PEKIM**  
 Email: njengapekim@gmail.com 
 Phone: +254 797933409
 GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)
