### NAME OF THE WEBSITE 
ilikeitproperties
### BRANCH 
Staging
### PROJECT'S BRIEF DESCRIPTION
A dynamic real estate website built with Flask, HTML, Bootstrap 5 classes and CSS, designed to showcase property listings and blog posts and also for users to make inquiries about the listings. The site is divided into two main interfaces:

-User Interface – Public-facing pages for browsing listings, making inquiries about the listings or any other matter, reading blogs, and learning about the company

-Admin Interface – Secure backend for managing listings and blog content (add/update/delete)

### TOOLS USED
- Flask
- HTML
- CSS
- Bootstrap 5
- Cloudflare r2 - For hosting my images and other static files
- Render - Hosting my website
- Neon - Hosting my database
- Github Copilot

### PROJECT'S STRUCTURE
real-estate-website/
├── config.py
├── confirm_images.py
├── README.md
├── requirements.txt
├── run.py
├── render.yml
├── Dockerfile
├── set_admin.py
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
Used Render's auto-deploy each time I make a push to github

### Setup
1. Created a web service on render
  - Selected a Python environment
  - Linked my service to the staging branch of my Github repo
  - Added environment variables
  - Defined Build and Start commands
2. Created a render.yml file(contains instructions on how my code will be deployed on render)
3. Pushed my code to the master's branch(staging branch) of my github repository
4. Render auto-deploys the code

🚀 Deployment Strategy (Staging)
This staging branch uses Render’s auto-deploy feature to automatically build and deploy the website whenever code is pushed to GitHub.

🔧 Setup Steps
1.Created a Web Service on Render
  - Selected the Python environment
  - Linked the service to the master branch of your GitHub repository (used as your staging branch)
  - Added required environment variables via the Render dashboard
  - Defined:
    Build command: pip install -r requirements.txt
    Start command: gunicorn run:app

2.Created a render.yml File
  - This file contains declarative instructions for Render to:
  - Identify the service type (web)
  - Enable auto-deploy on commit
  - It ensures consistent deployment behavior across environments

3. Pushed Code to GitHub
  - Code is pushed to the master branch (used as staging)
  - Render detects the change and automatically:
  - Installs dependencies
  - Runs the start command
  - Deploys the app to: https://ilikeitproperties.onrender.com



##  Developer Contact
Developed and maintained by **PEKIM**  
 Email: njengapekim@gmail.com 
 Phone: +254 797933409
 GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)

